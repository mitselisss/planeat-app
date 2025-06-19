from django.core.management.base import BaseCommand
from django.db import transaction, models
from app.models import Meal
import heapq
import random
from typing import Dict, List, Tuple, DefaultDict
from collections import defaultdict
import pandas as pd
from itertools import islice
import numpy as np
from django.db.models import Q
from itertools import combinations

# Constants
N_DAILY_PLANS = 10000
TOP_PLANS = 20
NUTRIENT_TOLERANCE = 0.1
MEAL_TYPES = ["Breakfast", "Snack", "Lunch", "Snack", "Dinner"]
FOOD_GROUP_MAPPING = {
    'MA': ('mea',), 'MAA': ('mea',), 'MAC': ('mea',), 'MAE': ('mea',),
    'MAG': ('mea',), 'MAI': ('mea',), 'MC': ('mea',), 'MCA': ('mea',),
    'MCC': ('mea',), 'MCE': ('mea',), 'MCG': ('mea',), 'MI': ('mea',),
    'DF': ('veg',), 'DG': ('veg',), 'DI': ('veg',), 'DR': ('veg',),
    'F': ('fru',), 'FA': ('fru',), 'FC': ('jui',), 'DB': ('plp',),
    'BA': ('dai',), 'BC': ('dai',), 'BL': ('che', 'dai'), 'BN': ('dai',),
    'G': ('nns',), 'GA': ('nns',), 'J': ('fis',), 'JA': ('fis',),
}

class NutritionCalculator:
    @staticmethod
    def calculate(meals: List[Meal]) -> Dict[str, float]:
        nutrition = defaultdict(float)
        food_groups = defaultdict(lambda: {'servings': 0, 'grams': 0})
        
        for meal in meals:
            for nutrient in ['Total_Energy', 'Total_Protein', 'Total_Carbs',
                            'Total_Fat', 'Total_Fibre', 'Total_Calcium',
                            'Total_Iron', 'Total_Folate']:
                nutrition[nutrient[6:].lower()] += getattr(meal, nutrient)
            
            for group_info in meal.Food_Groups_Counter:
                group_code, servings, grams = group_info[:3]
                category = FOOD_GROUP_MAPPING.get(group_code, (None,))[0]
                if category:
                    food_groups[f"{category}_s"]['servings'] += servings
                    food_groups[f"{category}_q"]['grams'] += grams
        
        for category, values in food_groups.items():
            nutrition[category] = values['grams'] if category.endswith('_q') else values['servings']
        
        return nutrition

class MealFilter:
    PREFERENCE_FILTERS = {
        "pescatarian": Q(Meat=0),
        "vegetarian": Q(Meat=0) & Q(Fish=0),
        "vegan": Q(Meat=0) & Q(Fish=0) & Q(Dairy=0),
    }
    
    ALLERGY_FILTERS = {
        "milk_allergy": Q(Dairy=0),
        "nuts_allergy": Q(Nuts_and_seeds=0),
    }

    @classmethod
    def filter(cls, queryset, preferences, allergies):
        q = cls.PREFERENCE_FILTERS.get(preferences, Q())
        if allergies in cls.ALLERGY_FILTERS:
            q &= cls.ALLERGY_FILTERS[allergies]
        return queryset.filter(q)

class BaseMealGenerator:
    NUTRITION_WEIGHTS = {
        "energy": 1, "protein": 0.08, "carb": 0.08, "fat": 0.08,
        "fibre": 0.06, "calcium": 0.1, "iron": 0.1, "folate": 0.1,
        "mea_q": 0.1, "mea_s": 0.1, "veg_q": 0.04, "veg_s": 0.02,
        "fru_q": 0.04, "fru_s": 0.2, "plp_q": 0.06, "dai_q": 0.02,
        "dai_s": 0.01, "che_q": 0.02, "che_s": 0.01, "nns_q": 0.06,
        "fis_q": 0.1, "fis_s": 0.1,
    }

    def __init__(self, user_settings):
        self.user = user_settings
        self.meal_counts = defaultdict(int)

    def _in_range(self, value, target, tolerance=0.1):
        return target * (1 - tolerance) <= value <= target * (1 + tolerance)

class DailyMealPlanGenerator(BaseMealGenerator):
    def __init__(self, user_settings):
        super().__init__(user_settings)
        self.energy_target = user_settings['energy']
        self.protein_target = user_settings['weight'] * 0.83
        self.meals = self.load_meals()

    def load_meals(self):
        base_qs = Meal.objects.filter(Country__in=self.user['country'])
        filtered = MealFilter.filter(base_qs, self.user['preferences'], self.user['allergies'])
        return [filtered.filter(Type=t) for t in MEAL_TYPES]

    def generate_plans(self):
        meal_groups = self.meals
        size_estimates = [mg.count() for mg in meal_groups]
        total_combo = np.prod(size_estimates)
        
        if total_combo > N_DAILY_PLANS:
            combos = (random.choices(mg, k=5) for mg in meal_groups)
            samples = zip(*combos)
        else:
            samples = product(*meal_groups)
        
        heap = []
        for idx, combo in enumerate(islice(samples, N_DAILY_PLANS)):
            self.process_combo(idx, combo, heap)
        
        #return sorted(heap, key=lambda x: -x['score'])[:TOP_PLANS]
        return sorted([plan[2] for plan in heap], key=lambda x: -x["score"])

    def _update_meal_counts(self, meal_ids: List[int], increment: bool):
        """NEW: Properly handle meal count updates"""
        delta = 1 if increment else -1
        for i, m in enumerate(meal_ids):
            #if i in [0, 2, 4]:  # Only track main meals
            self.meal_counts[m] += delta

    def process_combo(self, idx, combo, heap):
        meal_ids = tuple(m.id for m in combo)
        nutrition = NutritionCalculator.calculate(combo)
        score = self.calculate_score(nutrition)
        
        penalty = sum(self.meal_counts[mid] for mid in meal_ids) * 0.1
        final_score = score - penalty
        
        entry = (score, idx, {
            'meals': meal_ids,
            'score': final_score,
            'nutrition': nutrition,
        })

        # if all(self.meal_counts[m] < 5 for m in meal_ids):
        #     if len(heap) <= TOP_PLANS:
        #         heapq.heappush(heap, entry)
        #         self._update_meal_counts(meal_ids, increment=True)
        #     else:
        #         if final_score > heap[0][0]:
        #             removed = heapq.heappop(heap)
        #             self._update_meal_counts(removed[2]["meals"], increment=False)
        #             heapq.heappush(heap, entry)
        #             self._update_meal_counts(meal_ids, increment=True)
        
        if len(heap) < TOP_PLANS or final_score > heap[0]['score']:
            self.update_heap(heap, entry)
            self.update_meal_counts(meal_ids, len(heap) >= TOP_PLANS)

    def update_heap(self, heap, entry):
        """Maintain a min-heap of fixed size with highest scoring entries"""
        if len(heap) < TOP_PLANS:
            heapq.heappush(heap, entry)
        else:
            # Efficiently check and replace in one operation
            heapq.heappushpop(heap, entry)

    def update_meal_counts(self, meal_ids, is_replacement):
        """Update meal occurrence counts with atomic operations"""
        delta = 1
        if is_replacement:
            # Will decrement old meals when they're popped from heap
            return  # Defer decrement until actual replacement
        
        # Simple increment for new meals
        for meal_id in meal_ids:
            self.meal_counts[meal_id] = self.meal_counts.get(meal_id, 0) + 1
                
    def calculate_score(self, nutrition):
        score = 0
        score += self._score_energy(nutrition)
        score += self._score_macronutrients(nutrition)
        score += self._score_micronutrients(nutrition)
        score += self._score_food_groups(nutrition)
        return score

    def _score_energy(self, nutrition):
        energy = nutrition.get('energy', 0)
        if self._in_range(energy, self.energy_target, 0.05):
            return 10 * self.NUTRITION_WEIGHTS['energy']
        if self._in_range(energy, self.energy_target, 0.1):
            return 5 * self.NUTRITION_WEIGHTS['energy']
        return 0

    def _score_macronutrients(self, nutrition):
        score = 0
        # Protein scoring
        protein_target = self.protein_target
        if self._in_range(nutrition.get("protein", 0), protein_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["protein"]
        elif self._in_range(nutrition.get("protein", 0), protein_target, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["protein"]

        # Carb scoring
        if 0.45*self.energy_target/4 <= nutrition.get("carb", 0) <= 0.6*self.energy_target/4:
            score += 10 * self.NUTRITION_WEIGHTS["carb"]
            nutrition["carb_variable"] = 10

        # Fats scoring
        if 0.2*self.energy_target/9 <= nutrition.get("fat", 0) <= 0.35*self.energy_target/9:
            score += 10 * self.NUTRITION_WEIGHTS["fat"]

        # Fibre scoring
        if nutrition.get("fibre", 0) > 22.5:
            score += 10 * self.NUTRITION_WEIGHTS["fibre"]
        elif nutrition.get("fibre", 0) > 20:
            score += 5 * self.NUTRITION_WEIGHTS["fibre"]
        return score

    def _score_micronutrients(self, nutrition):
        score = 0

        # Calcuim scoring
        calcium_target = 1000
        if self._in_range(nutrition.get("calcium", 0), calcium_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["calcium"]
        elif self._in_range(nutrition.get("calcium", 0), calcium_target, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["calcium"]

        # Iron scoring
        # if use.sex == 'Male':
        #     iron_target = 11
        # elif user.sex == 'Female':
        #     iron_target = 17
        iron_target = 11
        if self._in_range(nutrition.get("iron", 0), iron_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["iron"]
        elif self._in_range(nutrition.get("iron", 0), iron_target, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["iron"]

        # Folate scoring
        folate_target = 330
        if self._in_range(nutrition.get("folate", 0), folate_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["folate"]
        elif self._in_range(nutrition.get("folate", 0), folate_target, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["folate"]
        return score

    def _score_food_groups(self, nutrition):
        score = 0

        # Vegetable quantity scoring
        nutrition["veg_q_variable"] = 0
        nutrition["veg_q_prediction"] = nutrition.get("veg_q", 0)
        if nutrition.get("veg_q", 0) > 270:
            score += 10 * self.NUTRITION_WEIGHTS["veg_q"]
            nutrition["veg_q_variable"] = 10
        elif nutrition.get("veg_q", 0) > 240:
            score += 5 * self.NUTRITION_WEIGHTS["veg_q"]
            nutrition["veg_q_variable"] = 5

        # Vegetable serving scoring
        nutrition["veg_s_variable"] = 0
        nutrition["veg_s_prediction"] = nutrition.get("veg_s", 0)
        if nutrition.get("veg_s", 0) > 2:
            score += 10 * self.NUTRITION_WEIGHTS["veg_s"]
            nutrition["veg_s_variable"] = 10
        elif nutrition.get("veg_s", 0) > 1:
            score += 5 * self.NUTRITION_WEIGHTS["veg_s"]
            nutrition["veg_s_variable"] = 5

        # Fruit quantity scoring
        fruit_quantity_variable = 0
        fruit_quantity_target = 200
        nutrition["fru_q_variable"] = 0
        nutrition["fru_q_prediction"] = nutrition.get("fru_q", 0)
        if self._in_range(nutrition.get("fru_q", 0), fruit_quantity_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["fru_q"]
            nutrition["fru_q_variable"] = 10
        elif self._in_range(nutrition.get("fru_q", 0), fruit_quantity_target, 0.1):
            score += 5 * self.NUTRITION_WEIGHTS["fru_q"]
            nutrition["fru_q_variable"] = 5
        
        # Fruit serving scoring
        fruit_serving_target = 2
        nutrition["fru_s_variable"] = 0
        nutrition["fru_s_prediction"] = nutrition.get("fru_s", 0)
        if nutrition.get("fru_s", 0) == fruit_serving_target:
            score += 10 * self.NUTRITION_WEIGHTS["fru_s"]
            nutrition["fru_s_variable"] = 10
        elif fruit_serving_target-1 <= nutrition.get("fru_s", 0) <= fruit_serving_target+1:
            score += 5 * self.NUTRITION_WEIGHTS["fru_s"]
            nutrition["fru_s_variable"] = 5

        # Juice serving scoring
        juice_serving_target = 1
        nutrition["jui_s_variable"] = 0
        nutrition["jui_s_prediction"] = nutrition.get("jui_s", 0)
        if nutrition.get("Jui_s", 0) > juice_serving_target:
            score += -1 * self.NUTRITION_WEIGHTS["jui_s"]
            nutrition["jui_s_variable"] = -1

        # Plant protein quantity scoring
        nutrition["plp_q_variable"] = 0
        nutrition["plp_q_prediction"] = nutrition.get("plp_q", 0)
        if nutrition.get("plp_q", 0) > 112.5:
            score += 10 * self.NUTRITION_WEIGHTS["plp_q"]
            nutrition["plp_q_variable"] = 10
        elif nutrition.get("plp_q", 0) > 100:
            score += 5 * self.NUTRITION_WEIGHTS["plp_q"]
            nutrition["plp_q_variable"] = 5

        # Dairy quantity scoring
        nutrition["dai_q_variable"] = 0
        nutrition["dai_q_prediction"] = nutrition.get("dai_q", 0)
        if 125 <= nutrition.get("dai_q", 0) <= 250:
            score += 10 * self.NUTRITION_WEIGHTS["dai_q"]
            nutrition["dai_q_variable"] = 10
        
        # Dairy serving scoring
        nutrition["dai_s_variable"] = 0
        nutrition["dai_s_prediction"] = nutrition.get("dai_s", 0)
        if 1 <= nutrition.get("dai_s", 0) <= 2:
            score += 10 * self.NUTRITION_WEIGHTS["dai_s"]
            nutrition["dai_s_variable"] = 10

        # Cheese quantity scoring
        cheese_quantity_ratget = 25
        nutrition["che_q_variable"] = 0
        nutrition["che_q_prediction"] = nutrition.get("che_q", 0)
        if self._in_range(nutrition.get("che_q", 0), cheese_quantity_ratget, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["che_q"]
            nutrition["che_q_variable"] = 10
        elif self._in_range(nutrition.get("che_q", 0), cheese_quantity_ratget, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["che_q"]
            nutrition["che_q_variable"] = 5
        
        # Cheese serving scoring
        cheese_serving_ratget = 1
        nutrition["che_s_variable"] = 0
        nutrition["che_s_prediction"] = nutrition.get("che_s", 0)
        if nutrition.get("che_s", 0) == 1:
            score += 10 * self.NUTRITION_WEIGHTS["che_s"]
            nutrition["che_s_variable"] = 10

        # Nuts and seeds quantity scoring
        nuts_and_seeds_quantity_target = 30
        nutrition["nns_q_variable"] = 0
        nutrition["nns_q_prediction"] = nutrition.get("nns_q", 0)
        if self._in_range(nutrition.get("nns_q", 0), nuts_and_seeds_quantity_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["nns_q"]
            nutrition["nns_q_variable"] = 10
        elif self._in_range(nutrition.get("nns_q", 0), nuts_and_seeds_quantity_target, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["nns_q"]
            nutrition["nns_q_variable"] = 5

        # Add meat to nutrition dictionary
        nutrition["mea_q_prediction"] = nutrition.get("mea_q", 0)
        nutrition["mea_s_prediction"] = nutrition.get("mea_s", 0)

        # Add fish to nutrition dictionary
        nutrition["fis_q_prediction"] = nutrition.get("fis_q", 0)
        nutrition["fis_s_prediction"] = nutrition.get("fis_s", 0)

        return score

class WeeklyMealPlanGenerator(BaseMealGenerator):
    def generate_plans(self, daily_plans):
        if len(daily_plans) < 7:
            print("Insufficient daily plans (need ≥7) to generate weekly plans")
            return []

        # Generate reasonable combinations using sliding window
        weekly_combos = (daily_plans[i:i+7] for i in range(len(daily_plans) - 6))
        
        return heapq.nlargest(
            TOP_PLANS,
            (self.score_week(combo) for combo in weekly_combos),
            key=lambda x: x['score']
        )

    # def generate_plans(self, daily_plans):
    #     return heapq.nlargest(
    #         TOP_PLANS,
    #         (self.score_week(combo) for combo in combinations(daily_plans, 7)),
    #         key=lambda x: x['score']
    #     )

class Command(BaseCommand):
    help = 'Generate optimized meal plans'
    
    def handle(self, *args, **kwargs):
        user_settings = {
            'weight': 80,
            'energy': 2200,
            'country': ["Ireland"],
            'preferences': "vegan",
            'allergies': "milk_allergy"
        }
        
        daily_gen = DailyMealPlanGenerator(user_settings)
        daily_plans = daily_gen.generate_plans()
        self.analyze_results(daily_plans, 'Daily')
        print("###################")
        weekly_gen = WeeklyMealPlanGenerator(user_settings)
        weekly_plans = weekly_gen.generate_plans(daily_plans)
        self.analyze_results(weekly_plans, 'Weekly')

    
    def analyze_results(self, results, plan_type):
        if not results:
            print(f"\n{plan_type} Plans Analysis: No valid plans generated")
            return

        try:
            df = pd.DataFrame([{
                'Score': r['score'],
                **{k: v for k, v in r['nutrition'].items() if not k.endswith('_variable')}
            } for r in results if r and 'nutrition' in r and 'score' in r])
            
            if df.empty:
                print(f"\n{plan_type} Plans Analysis: Data exists but couldn't create DataFrame")
                return

            print(f"\n{plan_type} Plans Analysis:")
            print(df.describe().T[['mean', 'min', 'max']].fillna(0))
            
        except Exception as e:
            print(f"\nError analyzing {plan_type.lower()} plans:")
            print(f"Type: {type(e).__name__}")
            print(f"Message: {str(e)}")
            print("Sample of problematic data:")
            print(results[:1])  # Show first entry for debugging
    
    
    # def analyze_results(self, results, plan_type):
    #     df = pd.DataFrame([{
    #         'Score': r['score'],
    #         **{k: v for k, v in r['nutrition'].items() if not k.endswith('_variable')}
    #     } for r in results])
    #     print(f"\n{plan_type} Plans Analysis:")
    #     print(df.describe().T[['mean', 'min', 'max']])