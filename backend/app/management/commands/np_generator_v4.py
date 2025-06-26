import random
import numpy as np
import pandas as pd

from django.core.management.base import BaseCommand
from django.db import models
from django.db.models import Q
from app.models import Meal
from random import sample
from typing import Dict, List, Tuple, Iterator
from itertools import combinations
from collections import defaultdict
from datetime import date

pd.options.display.float_format = '{:.3f}'.format
np.set_printoptions(suppress=True, formatter={'all': lambda x: f'{x:.6f}'})


def print_results(daily: List, daily_targets, weekly: List, weekly_targets, weights):
    def flatten_plans(plans):
        rows = []
        for entry in plans:
            row = {
                'DNPS': entry['DNPS'],
                'NDNPS': entry['NDNPS'],
            }
            row.update(entry['nutrition'])
            rows.append(row)
        return pd.DataFrame(rows).sort_values('NDNPS')

    df_daily = flatten_plans(daily)
    df_weekly = flatten_plans(weekly)

    print("\n--- DAILY TARGETS ---")
    print(daily_targets)
    print("\n--- DAILY PLANS ANALYSIS ---")
    print(df_daily.head(10))  # only top 10 for quick view

    print("\n--- WEEKLY TARGETS ---")
    print(weekly_targets)
    print("\n--- WEEKLY PLANS ANALYSIS ---")
    print(df_weekly.head(10))


def return_best_plan(user_settings):
    daily_gen = DailyMealPlanGenerator(user_settings)
    daily_plans = daily_gen.process()
    if len(daily_plans) == 0:
        print(f'No daily plans found due to nutritional rules, likely jui_s > 1')
        return None, -2
    daily_targets = daily_gen.targets

    weekly_gen = WeeklyMealPlanGenerator(daily_plans, user_settings)
    weekly_plans = weekly_gen.process()
    if len(weekly_plans) == 0:
        print(f'No weekly plans found due to nutritional rules, likely blv_s > 1')
        return None, -3
    weekly_targets = weekly_gen.targets

    best_plan, divercity_depth = Divercity(weekly_plans).process()

    # Commend the two lines bolow if you want to run the command for virtual users' testing or uncomment them to run in the backend.
    #print_results(daily_plans, daily_targets, weekly_plans, weekly_targets, daily_gen.NUTRITION_WEIGHTS)
    return best_plan # Commend this line if you want to run the command for virtual users' testing.

    return get_best_meal(
        user_settings['a/a'],
        daily_plans,
        best_plan,
        daily_targets,
        weekly_targets,
        divercity_depth,
        user_settings['sex'],
        user_settings['preference'],
        user_settings['allergy']), 0


def get_best_meal(aa, daily_plans, best_plan, daily_targets, weekly_targets, divercity_depth, sex, preference, allergy):
    row = {
        'a/a': aa,
        'dd': divercity_depth,
        'sex': sex,
        'preference': preference,
        'allergy': allergy,
    }

    for i, idx in enumerate(best_plan['idx']):
        dnp = next((d for d in daily_plans if d['idx'] == idx), None)
        for nutrient, value in dnp['nutrition'].items():
            row[f"day_{i+1}_{nutrient}"] = value
        for key, value in daily_targets.items():
            row[f'day_{i+1}_{key}_target'] = value
        row[f'day_{i+1}_DNSP'] = dnp['DNPS']
        row[f'day_{i+1}_NDNSP'] = dnp['NDNPS']

    for nutrient, value in best_plan['nutrition'].items():
        row[f'week_{nutrient}'] = value
    for key, value in weekly_targets.items():
        row[f'week_{key}_target'] = value
    row[f"DNPS"] = best_plan['DNPS']
    row[f"NDNPS"] = best_plan['NDNPS']

    return row


class BaseFunctions:
    def __init__(self, user_settings: Dict, is_daily=False):
        self.user_settings = user_settings
        self.is_daily = is_daily
        self._set_targets()
        self.fields = [
            'Total_Energy',
            'Total_Protein', 'Total_Fat',
            'Total_Carbs',
            'Total_Fibre',
            'Total_Calcium', 'Total_Iron', 'Total_Folate',
            'veg_q', 'veg_s',
            'fru_q', 'fru_s',
            'jui_s',
            'leg_q',
            'dai_q', 'dai_s',
            'che_q', 'che_s',
            'nns_q',
            'mea_q', 'mea_s',
            'blv_q', 'blv_s',
            'fis_q', 'fis_s',
            'oif_q', 'oif_s',
        ]

    def _set_targets(self):
        if self.is_daily:
            base = self.user_settings["base_energy"]
            current = self.user_settings["energy_intake"]
            self.targets = {
                'Total_Energy': current,
                'Total_Protein': (current*0.15/4, current*0.25/4),
                'Total_Fat': (current*0.2/9, current*0.35/9),
                'Total_Carbs': (current*0.45/4, current*0.6/4),
                'Total_Fibre': current*25/base,
                'Total_Calcium': current*1000/base,
                'Total_Iron': current*11/base if self.user_settings["sex"] == "Female" else current*17/base,
                'Total_Folate': current*330/base,
                'veg_q': current*300/base,
                'veg_s': 3,
                'fru_q': current*200/base,
                'fru_s': 2,
                'jui_s': 1,
                'leg_q': current*125/base,
                'dai_q': (current*125/base, current*250/base),
                'dai_s': (1, 2),
                'che_q': current*25/base,
                'che_s': 1,
                'nns_q': current*30/base,
            }
            self.NUTRITION_WEIGHTS = {
                'Total_Energy': 0.3,
                'Total_Protein': 0.8,
                'Total_Fat': 0.04,
                'Total_Carbs': 0.04,
                'Total_Fibre': 0.04,
                'Total_Calcium': 0.04,
                'Total_Iron': 0.04,
                'Total_Folate': 0.02,
                'veg_q': 0.06,
                'veg_s': 0.02,
                'fru_q': 0.06,
                'fru_s': 0.02,
                'jui_s': 0,
                'leg_q': 0.1,
                'dai_q': 0.04,
                'dai_s': 0.01,
                'che_q': 0.02,
                'che_s': 0.01,
                'nns_q': 0.06,
            }
        else:
            base = self.user_settings["base_energy"]
            current = self.user_settings["energy_intake"]*7
            self.targets = {
                'Total_Energy': current,
                'Total_Protein': (current*0.15/4, current*0.25/4),
                'Total_Fat': (current*0.2/9, current*0.35/9),
                'Total_Carbs': (current*0.45/4, current*0.6/4),
                'Total_Fibre': current*25/base,
                'Total_Calcium': current*1000/base,
                'Total_Iron': current*11/base if self.user_settings["sex"] == "Female" else current*17/base,
                'Total_Folate': current*330/base,
                'veg_q': current*300/base,
                'veg_s': 3*7,
                'fru_q': current*200/base,
                'fru_s': 2*7,
                'jui_s': 1*7,
                'leg_q': current*125/base,
                'dai_q': (current*125/base, current*250/base),
                'dai_s': (1*7, 2*7),
                'che_q': current*25/base,
                'che_s': 1*7,
                'nns_q': current*30/base,
                'mea_q': (current/7)*420/base,
                'mea_s': 3,
                'blv_q': (current/7)*140/base,
                'blv_s': 1,
                'fis_q': (current/7)*200/base,
                'fis_s': 2,
                'oif_q': (current/7)*100/base,
                'oif_s': 1,
            }
            self.NUTRITION_WEIGHTS = {
                'Total_Energy': 0.3,
                'Total_Protein': 0.8,
                'Total_Fat': 0.04,
                'Total_Carbs': 0.04,
                'Total_Fibre': 0.04,
                'Total_Calcium': 0.04,
                'Total_Iron': 0.04,
                'Total_Folate': 0.02,
                'veg_q': 0.04,
                'veg_s': 0.01,
                'fru_q': 0.04,
                'fru_s': 0.01,
                'jui_s': 0,
                'leg_q': 0.1,
                'dai_q': 0.02,
                'dai_s': 0.01,
                'che_q': 0.01,
                'che_s': 0.01,
                'nns_q': 0.05,
                'mea_q': 0.02,
                'mea_s': 0.01,
                'blv_q': 0.01,
                'blv_s': 0.01,
                'fis_q': 0.02,
                'fis_s': 0.01,
                'oif_q': 0.01,
                'oif_s': 0.01,
            }

    def _filtering(self):
        '''
        Function that filters the whole meals' database based on:
        seasonality, user's preferences, user's allergies, and
        cuisine county/countries
        '''

        current_month = int(str(date.today()).split('-')[1])  # Get current moth.
        season = (
            "winter" if current_month in [12, 1, 2] else
            "spring" if current_month in [3, 4, 5] else
            "summer" if current_month in [6, 7, 8] else
            "autumn"
        )

        SEASSON_FILTERS = {
            "autumn": Q(Autumn="Y"),
            "winter": Q(Winter="Y"),
            "spring": Q(Spring="Y"),
            "summer": Q(Summer="Y"),
        }

        PREFERENCE_FILTERS = {
            "pescatarian": ~Q(Meat__gt=0),  # Exclude meals where Meat > 0
            "vegetarian": ~Q(Meat__gt=0) & ~Q(Fish__gt=0),  # Exclude Meat and Fish
            "vegan": ~Q(Meat__gt=0) & ~Q(Fish__gt=0) & ~Q(Dairy__gt=0),  # Exclude Meat, Fish, and Dairy
        }


        ALLERGY_FILTERS = {
            "milk_allergy": ~Q(Dairy__gt=0),
            "nuts_allergy": ~Q(Nuts_and_seeds__gt=0),
            "milk_nuts_allergy": ~Q(Dairy__gt=0) & ~Q(Nuts_and_seeds__gt=0)
        }

        query = (
            SEASSON_FILTERS[season] &
            Q(Country__in=self.user_settings['cuisine']) &
            PREFERENCE_FILTERS.get(self.user_settings['preference'], Q()) &  # Default to empty Q if preference not found
            ALLERGY_FILTERS.get(self.user_settings['allergy'], Q())  # Default to empty Q if allergy not found
        )

        return list(Meal.objects.filter(query).values(*self.fields, 'Type', 'id'))

    def _get_five_meals(self, meals):
        breakfast = [m for m in meals if m['Type'] == "Breakfast"]
        snack = [m for m in meals if m['Type'] == "Snack"]
        lunch = [m for m in meals if m['Type'] == "Lunch"]
        dinner = [m for m in meals if m['Type'] == "Dinner"]

        return [breakfast, snack, lunch, snack, dinner]

    def batch_score(self, daily_totals):
        num_samples, num_nutrients = daily_totals.shape
        score_matrix = np.zeros((num_samples, num_nutrients), dtype=np.float32)

        for i, nutrient in enumerate(self.fields):
            weight = self.NUTRITION_WEIGHTS.get(nutrient, 0.0)
            target = self.targets.get(nutrient, 0.0)
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
        weights = np.array([self.NUTRITION_WEIGHTS.get(f, 0.0) for f in self.fields], dtype=np.float32)
        weighted_squared = (score_matrix ** 2) * weights  # shape: (n_samples, n_fields)
        dnps = np.sqrt(np.sum(weighted_squared, axis=1))
        ndnps = dnps / (dnps + 1.0)
        return dnps, ndnps


class DailyMealPlanGenerator(BaseFunctions):
    def __init__(self, user_settings):
        super().__init__(user_settings, is_daily=True)
        self.sample_size = 100000

    def generate_combinations(self, meal_groups: List[list]) -> list:
        group_lens = [len(group) for group in meal_groups]
        total_combos = np.prod(group_lens)

        sample_size = min(self.sample_size, total_combos)

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

    def calculate_nutrition(self, meals):
        # meals is a tuple of 5 dicts
        return {
            field: sum(m[field] for m in meals)
            for field in self.fields
        }

    def batch_calculate_nutrition(self, combos):
        # Step 1: convert combos to a 3D NumPy array
        # combos: list of tuples (each: 5 dicts), len = 100,000
        field_list = self.fields
        num_fields = len(field_list)
        num_combos = len(combos)

        # Create the array (100000, 5, num_fields)
        nutrition_array = np.zeros((num_combos, 5, num_fields), dtype=np.float32)

        field_idx = {field: i for i, field in enumerate(field_list)}

        for i, combo in enumerate(combos):
            for j, meal in enumerate(combo):  # 5 meals
                for field in field_list:
                    nutrition_array[i, j, field_idx[field]] = meal.get(field, 0)

        # Step 2: Sum across the 5 meals → daily totals
        daily_totals = nutrition_array.sum(axis=1)  # shape: (100000, num_fields)

        return daily_totals, field_list  # You’ll need fields for scoring

    def process(self):
        meals = self._filtering()
        print("--->", len(meals))
        meal_groups = self._get_five_meals(meals)
        print("--->", len(meal_groups[0]), len(meal_groups[1]), len(meal_groups[2]), len(meal_groups[3]),len(meal_groups[4]))
        combos = self.generate_combinations(meal_groups)  # list of 100,000 tuples of 5 meals
        print("--->", len(combos))

        # 1. Batch calculate nutrition for all combos
        daily_totals, field_list = self.batch_calculate_nutrition(combos)

        # 2. Optionally: Apply your jui_s > 1 filter
        jui_s_index = field_list.index('jui_s')
        valid_mask = daily_totals[:, jui_s_index] <= 1
        daily_totals = daily_totals[valid_mask]
        filtered_combos = [c for i, c in enumerate(combos) if valid_mask[i]]

        # 3. Score all combos (placeholder, to be implemented next)
        score_matrix = self.batch_score(daily_totals)
        dnps, ndnps = self.batch_distance(score_matrix)

        # 4. Combine and sort
        top_k = 1000
        top_indices = np.argsort(ndnps)[:top_k]
        selected_indices = np.random.choice(top_indices, min(21, len(top_indices)), replace=False)

        final_plans = []
        for i in selected_indices:
            nutrition_dict = {field_list[j]: daily_totals[i, j] for j in range(len(field_list))}
            final_plans.append({
                "meals": [meal['id'] for meal in filtered_combos[i]],
                "idx": i,
                "DNPS": dnps[i],
                "NDNPS": ndnps[i],
                "nutrition": nutrition_dict
            })

        final_plans.sort(key=lambda x: x['NDNPS'])
        return final_plans


class WeeklyMealPlanGenerator(BaseFunctions):
    def __init__(self, daily_plans, user_settings):
        super().__init__(user_settings, is_daily=False)
        self.daily_plans = daily_plans
        self.nutrition_matrix = np.array([
            [plan['nutrition'][field] for field in self.fields]
            for plan in self.daily_plans
        ], dtype=np.float32)

        self.daily_indices = list(range(len(self.daily_plans)))
        self.daily_idx = []
        for idx in self.daily_plans:
            self.daily_idx.append(idx['idx'])

        # Create a mapping dictionary
        self.mapping = dict(zip(self.daily_indices, self.daily_idx))

    def _weekly_combinations_indices(self):
        return list(combinations(self.daily_indices, 7))

    def _batch_weekly_nutrition(self, combo_indices):
        # combo_indices: List of tuples (e.g., [(0,1,2,3,4,5,6), ...])
        num_combos = len(combo_indices)
        num_fields = self.nutrition_matrix.shape[1]
        weekly_totals = np.zeros((num_combos, num_fields), dtype=np.float32)

        for i, idxs in enumerate(combo_indices):
            weekly_totals[i] = self.nutrition_matrix[list(idxs)].sum(axis=0)

        return weekly_totals

    def _assemble_plans(self, combo_indices, weekly_totals, dnps, ndnps):
        final_weekly_plans = []
        top_k = 1000  # Or any number of weekly plans you want to consider
        top_indices = np.argsort(ndnps)[:top_k]

        for idx in top_indices:
            combo = combo_indices[idx]
            nutrition = {
                field: weekly_totals[idx, i]
                for i, field in enumerate(self.fields)
            }

            final_weekly_plans.append({
                "meals": [self.daily_plans[i]['meals'] for i in combo],
                "idx": [self.mapping[i] for i in list(combo)],
                "nutrition": nutrition,
                "DNPS": dnps[idx],
                "NDNPS": ndnps[idx],
            })

        return final_weekly_plans

    def process(self) -> List[Dict]:
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


class Divercity():
    def __init__(self, weekly_plans):
        self.weekly_plans = weekly_plans
        self.same_dishes = 3
        self.same_meals = 3

    def process(self):
        counter = 0
        for idx, wmp in enumerate(self.weekly_plans):
            meal_frequency = defaultdict(int)
            for day in wmp['meals']:
                for meal in day:
                    meal_frequency[meal] += 1
            if any(value >= self.same_meals for value in meal_frequency.values()):
                counter += 1
                continue
            #self.print_best_week(wmp, idx)
            return wmp, idx
        #self.print_best_week(self.weekly_plans[0], -1)
        return self.weekly_plans[0], -1

    def print_best_week(self, weekly_plan, dd):
        columns = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        rows = ['Breakfast', 'Morniing Snack', 'Lunch', 'Afternoon Snack', 'Dinner']
        df = pd.DataFrame(weekly_plan['meals'], columns, rows).transpose()
        print(f'Divercity depth: {dd}')
        print(df)


class Command(BaseCommand):
    help = 'Generate personalized weekly meal plans'

    def handle(self, *args, **kwargs):
        user_settings = self.set_user_profile()

        daily_gen = DailyMealPlanGenerator(user_settings)
        daily_plans = daily_gen.process()
        daily_targets = daily_gen.targets

        weekly_gen = WeeklyMealPlanGenerator(daily_plans, user_settings)
        weekly_plans = weekly_gen.process()
        weekly_targets = weekly_gen.targets

        print_results(daily_plans, daily_targets, weekly_plans, weekly_targets, daily_gen.NUTRITION_WEIGHTS)

        best_plan, dd = Divercity(weekly_plans).process()

    def set_user_profile(self):
        return {
            #'a/a': aa,
            'energy_intake': 3007.676618802675,
            'base_energy': 2500,
            'preference': 'omnivore',
            'allergy': 'milk_allergy',
            'cuisine': [
                #'Irish',
                #'Spain',
                'Hungary',
                ],
            'sex': 'male',
        }
