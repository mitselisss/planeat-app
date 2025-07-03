"""
Django command for generating vertual users for vasilis.
This command  uses a variation of the main recommender where only
kcal, protein, fats, and carbs are used in the objective function.
"""

import numpy as np
from app.models import Meal
from django.core.management.base import BaseCommand

field_list = [
    'Total_Energy', 'Total_Protein', 'Total_Fat', 'Total_Carbs',
]

NUTRITION_WEIGHTS = {
    'Total_Energy': 0.4,
    'Total_Protein': 0.2,
    'Total_Fat': 0.2,
    'Total_Carbs': 0.2,
}

class Command(BaseCommand):
    help = 'Generate virtual users for Vasilis'

    def _filtering(self, country):
        meals = Meal.objects.filter(Country__in=country).values_list(
            "Type", "Total_Energy", "Total_Protein", "Total_Fat", "Total_Carbs", "id"
        )

        dtype = np.dtype([
            ('Type', 'U20'),
            ('Total_Energy', 'f4'),
            ('Total_Protein', 'f4'),
            ('Total_Fat', 'f4'),
            ('Total_Carbs', 'f4'),
            ('id', 'i4'),
        ])
        return np.array(list(meals), dtype=dtype)

    def _get_five_meals(self, meals):
        breakfast = [m for m in meals if m['Type'] == "Breakfast"]
        snack = [m for m in meals if m['Type'] == "Snack"]
        lunch = [m for m in meals if m['Type'] == "Lunch"]
        dinner = [m for m in meals if m['Type'] in ["Dinner", "Evening Meal"]]

        return [breakfast, snack, lunch, snack, dinner]

    def normal_distr(self, mean, std):
        # Generate and return random calories for each user based in normal distribution.
        return np.random.normal(loc=mean, scale=std, size=5000)

    def _generate_combinations(self, meal_groups):
        group_lens = [len(group) for group in meal_groups]
        total_combos = np.prod(group_lens)

        sample_size = 100000
        sample_size = min(sample_size, total_combos)

        if total_combos == 0:
            return []  # Avoid generating if no combos possible

        group_arrays = [np.array(group) for group in meal_groups]

        # Sample with replacement if needed (e.g., some groups are very small)
        idx_matrix = [
            np.random.choice(len(group), size=sample_size, replace=True)
            for group in meal_groups
        ]

        combos = [group_arrays[i][idx_matrix[i]] for i in range(5)]
        return list(zip(*combos))  # List of tuples: (meal1, meal2, ..., meal5)

    def batch_calculate_nutrition(self, combos):
        # Step 1: convert combos to a 3D NumPy array
        # combos: list of tuples (each: 5 dicts), len = 100,000
        field_list = [
            'Total_Energy', 'Total_Protein', 'Total_Fat', 'Total_Carbs',
        ]
        num_fields = len(field_list)
        num_combos = len(combos)

        # Create the array (100000, 5, num_fields)
        nutrition_array = np.zeros((num_combos, 5, num_fields), dtype=np.float32)

        field_idx = {field: i for i, field in enumerate(field_list)}
        for i, combo in enumerate(combos):
            for j, meal in enumerate(combo):  # 5 meals
                for field in field_list:
                    nutrition_array[i, j, field_idx[field]] = meal[field]

        # Step 2: Sum across the 5 meals → daily totals
        daily_totals = nutrition_array.sum(axis=1)  # shape: (100000, num_fields)

        return daily_totals, field_list  # You’ll need fields for scoring

    def batch_score(self, daily_totals, user_kcal):
        num_samples, num_nutrients = daily_totals.shape
        score_matrix = np.zeros((num_samples, num_nutrients), dtype=np.float32)

        field_list = [
            'Total_Energy', 'Total_Protein', 'Total_Fat', 'Total_Carbs',
        ]
        targets = {
            'Total_Energy': user_kcal,
            'Total_Protein': (user_kcal*0.15/4, user_kcal*0.25/4),
            'Total_Fat': (user_kcal*0.2/9, user_kcal*0.35/9),
            'Total_Carbs': (user_kcal*0.45/4, user_kcal*0.6/4),
        }

        for i, nutrient in enumerate(field_list):
            weight = NUTRITION_WEIGHTS.get(nutrient, 0.0)
            target = targets.get(nutrient, 0.0)
            pred = daily_totals[:, i]

            if isinstance(target, tuple):
                lower, upper = target
                under = pred < lower
                over = pred > upper
                dist = np.zeros_like(pred)
                dist[under] = np.abs(pred[under] - lower)# / lower
                dist[over] = np.abs(pred[over] - upper)# / upper
            else:
                dist = np.abs(pred - target)# / target if target != 0 else 0

            score_matrix[:, i] = dist

        return score_matrix

    def batch_distance(self, score_matrix):
        # Vectorized weighted Euclidean distance
        weights = np.array([NUTRITION_WEIGHTS.get(f, 0.0) for f in field_list], dtype=np.float32)
        weighted_squared = (score_matrix ** 2) * weights  # shape: (n_samples, n_fields)
        dnps = np.sqrt(np.sum(weighted_squared, axis=1))
        ndnps = dnps / (dnps + 1.0)
        return dnps, ndnps

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting virtual users generation...')

        # Format float printing, skip strings
        np.set_printoptions(suppress=True, formatter={'float_kind': lambda x: f'{x:.6f}'})

        sets = [ [["Ireland"], 1527.35, 295.50], [["Spain"], 2387.32, 326.63], [["Hungary"], 1625.09, 281.10] ]
        for country, mean, std in sets:
            meals = self._filtering(country)
            #print(meals)

            meal_groups = self._get_five_meals(meals)
            if not all([len(meal_groups[0]), len(meal_groups[1]), len(meal_groups[2]), len(meal_groups[3]), len(meal_groups[4])]):
                print(f'Error with meals for countr {country}')
                continue

            for aa, user_kcal in enumerate(self.normal_distr(mean, std)):
                combos = self._generate_combinations(meal_groups)
                #print(len(combos))
                #print(combos[0])
                #quit()
                daily_totals, field_list = self.batch_calculate_nutrition(combos)
                #print(daily_totals)
                #print(field_list)

                score_matrix = self.batch_score(daily_totals, user_kcal)
                dnps, ndnps = self.batch_distance(score_matrix)

                top_k = 1000
                top_indices = np.argsort(ndnps)[:top_k]
                selected_indices = np.random.choice(top_indices, min(21, len(top_indices)), replace=False)

                final_plans = []
                for i in selected_indices:
                    nutrition_dict = {field_list[j]: daily_totals[i, j] for j in range(len(field_list))}

                    final_plans.append({
                        "meal_ids": [combo_meal['id'] for combo_meal in combos[i]],
                        "idx": i,
                        "DNPS": dnps[i],
                        "NDNPS": ndnps[i],
                        "nutrition": nutrition_dict
                    })

                final_plans.sort(key=lambda x: x['NDNPS'])
                print(f'Base: Total_Energy: {user_kcal}, Total_Protein: {(user_kcal*0.15/4, user_kcal*0.25/4)} Total_Fat: {(user_kcal*0.2/9, user_kcal*0.35/9)}, Total_Carbs: {(user_kcal*0.45/4, user_kcal*0.6/4)}')
                print(final_plans[0])

                combo_indices = self._weekly_combinations_indices()
                weekly_totals = self._batch_weekly_nutrition(combo_indices)

                # Filter by blv_s > 1
                blv_idx = self.fields.index('blv_s')
                valid_mask = weekly_totals[:, blv_idx] <= 1
                weekly_totals = weekly_totals[valid_mask]
                filtered_combo_indices = [combo_indices[i] for i, keep in enumerate(valid_mask) if keep]

                # Score
                score_matrix = self.batch_score(weekly_totals)
                dnps, ndnps = self.batch_distance(score_matrix)

                # Sort & return top
                return self._assemble_plans(filtered_combo_indices, weekly_totals, dnps, ndnps)

                quit()



        #self.stdout.write(self.style.SUCCESS('Virtual users generation ended.'))
