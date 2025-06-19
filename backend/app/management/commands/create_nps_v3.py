from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import Meal
import heapq
from random import sample
from typing import Dict, List, Tuple, Iterator
from itertools import product
from collections import defaultdict
import pandas as pd
from itertools import combinations
import random
from django.db.models import Q

N_MEAL_PLANS = 10000  # Reduced from 20,000 for initial testing
TOP_PLANS = 20
NUTRIENT_TOLERANCE = 0.1  # 10% tolerance for most nutrients
SAMPLE_SIZE = 10
NUMBER_OF_SAMPLES = 100000

class DailyMealPlanGenerator:
    # Configuration - could move to database model or settings
    NUTRITION_WEIGHTS = {
        "energy": 1,
        "protein": 0.08,
        "carb": 0.08,
        "fat": 0.08,
        "fibre": 0.06,
        "calcium": 0.1,
        "iron": 0.1,
        "folate": 0.1,
        "mea_q": 0.1,
        "mea_s": 0.1,
        "veg_q": 0.04,
        "veg_s": 0.02,
        "fru_q": 0.04,
        "fru_s": 0.2,
        "plp_q": 0.06,
        "dai_q": 0.02,
        "dai_s": 0.01,
        "che_q": 0.02,
        "che_s": 0.01,
        "nns_q": 0.06,
        "fis_q": 0.1,
        "fis_s": 0.1,
    }

    MEAL_TYPES = [
        "Breakfast",
        "Morning Snack",
        "Lunch",
        "Afternoon Snack",
        "Dinner"
    ]

    def __init__(self):
        self.user_weight = 80
        self.user_energy_intake = 3400
        self.user_country = ["Ireland"]
        self.user_preferences = "vegan"
        self.user_allergies = "milk_allergy"
        self.meal_counts = defaultdict(int)  # Track meal occurrences in heap

    def get_five_meals(self, meals):
        """Devide meals based on meal type"""
        meals = [
            meals.filter(Type="Breakfast"),
            meals.filter(Type="Snack"),
            meals.filter(Type="Lunch"),
            meals.filter(Type="Snack"),
            meals.filter(Type="Dinner")
        ]
        return meals


    def filter_meals_preferences_and_allergies(self, meals, preferences, allergies):
        '''
        Function that filters the meals based on user's preferences (Omnivorce, Pascaterian, Vegeterian, Vegan)
        and allergies (Dairy, Nuts).
        '''

        # preferences
        if preferences == "omnivore":
            print("omnivore")
            meals = meals
        elif preferences == "pescatarian":
            print("pescatarian")
            meals = meals.exclude(Q(Meat__gt=0))
            if len(meals) == 0: # Check for error for pescatarian.
                return None
        elif preferences == "vegetarian":
            print("vegetarian")
            meals = meals.exclude(Q(Meat__gt=0) | Q(Fish__gt=0))
            if len(meals) == 0:  # Check for error for vegetarian.
                return None
        elif preferences == "vegan":
            print("vegan")
            meals = meals.exclude(Q(Meat__gt=0) | Q(Fish__gt=0) | Q(Dairy__gt=0))
            if len(meals) == 0:  # Check for error for vegan.
                return None
        else:
            return None

        # allergies
        if allergies == "milk_allergy":
            print("milk_allergy")
            meals = meals.exclude(Dairy__gt=0)
            if len(meals) == 0:  # Check for error for omnivore/milk_allergy.
                return None
            return meals
        elif allergies == "nuts_allergy":
            print("nuts_allergy")
            meals = meals.exclude(Nuts_and_seeds__gt=0)
            if len(meals) == 0:  # Check for error for omnivore/nuts_allergy.
                return None
            return meals
        else:
            print("no allergies")
            return meals


    def load_meals(self, Country):
        """Load all meals based on user's restrictions"""
        filters = {
            "Country__in": Country
        }
        queryset = Meal.objects.filter().only(
                'id', 'Total_Energy', 'Total_Protein',
                'Total_Fat', 'Total_Carbs', 'Total_Fibre', 'Total_Calcium',
                'Total_Iron', 'Total_Folate', 'Food_Groups_Counter',
        )
        queryset = queryset.filter(Country__in=self.user_country)
        queryset = self.filter_meals_preferences_and_allergies(queryset, self.user_preferences, self.user_allergies)
        print("Final meals", len(queryset))
        return (queryset)

    def combinations(self, sets, num_samples):
        # Calculate the total number of possible combinations
        total_combinations = 1
        for s in sets:
            total_combinations *= len(s)

        # Generate random unique indices
        random_indices = random.sample(range(total_combinations), num_samples)

        # Define a function to get the combination at a specific index
        def get_combination_at_index(index):
            combination = []
            for s in reversed(sets):
                index, element_index = divmod(index, len(s))
                combination.append(list(s)[element_index])
            return tuple(reversed(combination))

        # Generate the combinations for the random indices
        random_combinations = [get_combination_at_index(index) for index in random_indices]
        return random_combinations

    def calculate_nutrition(self, meals: Tuple[Meal]) -> Dict[str, float]:
        """Aggregate nutritional values and food group totals from meals"""
        # Initialize nutrition sums
        nutrition_totals = {
            "energy": sum(m.Total_Energy for m in meals),
            "protein": sum(m.Total_Protein for m in meals),
            "carb": sum(m.Total_Carbs for m in meals),
            "fat": sum(m.Total_Fat for m in meals),
            "fibre": sum(m.Total_Fibre for m in meals),
            "calcium": sum(m.Total_Calcium for m in meals),
            "iron": sum(m.Total_Iron for m in meals),
            "folate": sum(m.Total_Folate for m in meals),
        }

        # Dictionary to store total servings and grams per food group
        food_group_totals = defaultdict(lambda: {"servings": 0, "grams": 0})

        # Process each meal to aggregate food group data
        for meal in meals:
            for food_group in meal.Food_Groups_Counter:
                group_code, servings, grams = food_group  # Unpack list values
                food_group_totals[group_code]["servings"] += servings
                food_group_totals[group_code]["grams"] += grams

        # Flatten food group totals into the final dictionary
        for group, totals in food_group_totals.items():
            if group in ["MA", "MAA", "MAC", "MAE", "MAG", "MAI", "MC", "MCA", "MCC", "MCE", "MCG", "MI",
                 "MCK", "MCM", "MCO", "ME", "MEA", "MEC", "MEE", "MG", "MBG", "MI", "MIG", "MR"]:
                nutrition_totals["mea_s"] = totals["servings"]
                nutrition_totals["mea_q"] = totals["grams"]
            if group in ["DF", "DG", "DI", "DR"]:
                nutrition_totals["veg_s"] = totals["servings"]
                nutrition_totals["veg_q"] = totals["grams"]
            if group in ["F", "FA"]:
                nutrition_totals["fru_s"] = totals["servings"]
                nutrition_totals["fru_q"] = totals["grams"]
            if group in ["FC"]:
                nutrition_totals["jui_s"] = totals["servings"]
                nutrition_totals["jui_q"] = totals["grams"]
            if group in ["DB"]:
                nutrition_totals["plp_s"] = totals["servings"]
                nutrition_totals["plp_q"] = totals["grams"]
            if group in ["BA", "BC", "BL", "BN"]:
                nutrition_totals["dai_s"] = totals["servings"]
                nutrition_totals["dai_q"] = totals["grams"]
            if group in ["BL"]:
                nutrition_totals["che_s"] = totals["servings"]
                nutrition_totals["che_q"] = totals["grams"]
            if group in ["G", "GA"]:
                nutrition_totals["nns_s"] = totals["servings"]
                nutrition_totals["nns_q"] = totals["grams"]
            if group in ["J", "JA", "JC", "JK", "JM", "JR"]:
                nutrition_totals["fis_s"] = totals["servings"]
                nutrition_totals["fis_q"] = totals["grams"]

        return nutrition_totals

    @staticmethod
    def _in_range(value: float, target: float, tolerance: float) -> bool:
        """Check if value is within target ± tolerance%"""
        return (target * (1 - tolerance)) <= value <= (target * (1 + tolerance))

    def score_meal_plan(self, nutrition: Dict[str, float]) -> float:
        """Modular scoring system with range checks"""
        score = 0.0

        # Energy scoring
        energy_target = self.user_energy_intake
        nutrition["energy_variable"] = 0
        nutrition["energy_prediction"] = nutrition.get("energy", 0)
        if self._in_range(nutrition.get("energy", 0), energy_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["energy"]
            nutrition["energy_variable"] = 10
        elif self._in_range(nutrition.get("energy", 0), energy_target, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["energy"]
            nutrition["energy_variable"] = 5

        # Protein scoring
        protein_target = self.user_weight * 0.83
        nutrition["protein_variable"] = 0
        nutrition["protein_prediction"] = nutrition.get("protein", 0)
        if self._in_range(nutrition.get("protein", 0), protein_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["protein"]
            nutrition["protein_variable"] = 10
        elif self._in_range(nutrition.get("protein", 0), protein_target, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["protein"]
            nutrition["protein_variable"] = 5

        # Carb scoring
        nutrition["carb_variable"] = 0
        nutrition["carb_prediction"] = nutrition.get("carb", 0)
        if 0.45*self.user_energy_intake/4 <= nutrition.get("carb", 0) <= 0.6*self.user_energy_intake/4:
            score += 10 * self.NUTRITION_WEIGHTS["carb"]
            nutrition["carb_variable"] = 10

        # Fats scoring
        nutrition["fat_variable"] = 0
        nutrition["fat_prediction"] = nutrition.get("fat", 0)
        if 0.2*self.user_energy_intake/9 <= nutrition.get("fat", 0) <= 0.35*self.user_energy_intake/9:
            score += 10 * self.NUTRITION_WEIGHTS["fat"]
            nutrition["fat_variable"] = 10

        # Fibre scoring
        nutrition["fibre_variable"] = 0
        nutrition["fibre_prediction"] = nutrition.get("fibre", 0)
        if nutrition.get("fibre", 0) > 22.5:
            score += 10 * self.NUTRITION_WEIGHTS["fibre"]
            nutrition["fibre_variable"] = 10
        elif nutrition.get("fibre", 0) > 20:
            score += 5 * self.NUTRITION_WEIGHTS["fibre"]
            nutrition["fibre_variable"] = 5

        # Calcuim scoring
        calcium_target = 1000
        nutrition["calcium_variable"] = 0
        nutrition["calcium_prediction"] = nutrition.get("calcium", 0)
        if self._in_range(nutrition.get("calcium", 0), calcium_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["calcium"]
            nutrition["calcium_variable"] = 10
        elif self._in_range(nutrition.get("calcium", 0), calcium_target, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["calcium"]
            nutrition["calcium_variable"] = 5

        # Iron scoring
        # if use.sex == 'Male':
        #     iron_target = 11
        # elif user.sex == 'Female':
        #     iron_target = 17
        iron_target = 11
        nutrition["iron_variable"] = 0
        nutrition["iron_prediction"] = nutrition.get("iron", 0)
        if self._in_range(nutrition.get("iron", 0), iron_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["iron"]
            nutrition["iron_variable"] = 10
        elif self._in_range(nutrition.get("iron", 0), iron_target, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["iron"]
            nutrition["iron_variable"] = 5

        # Folate scoring
        folate_target = 330
        nutrition["folate_variable"] = 0
        nutrition["folate_prediction"] = nutrition.get("folate", 0)
        if self._in_range(nutrition.get("folate", 0), folate_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["folate"]
            nutrition["folate_variable"] = 10
        elif self._in_range(nutrition.get("folate", 0), folate_target, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["folate"]
            nutrition["folate_variable"] = 5

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

    def _update_meal_counts(self, meal_ids: List[int], increment: bool):
        """NEW: Properly handle meal count updates"""
        delta = 1 if increment else -1
        for i, m in enumerate(meal_ids):
            #if i in [0, 2, 4]:  # Only track main meals
            self.meal_counts[m] += delta

    def process(self) -> List[Dict]:
        """Main processing pipeline"""
        top_plans = []
        temp_list = []
        meals = self.load_meals(self.user_country)
        meals = self.get_five_meals(meals)

        total_combinations = len(meals[0])*len(meals[1])*len(meals[2])*len(meals[3])*len(meals[4])
        print("Breakfasts:", len(meals[0]))
        print("Morning Snacks:", len(meals[1]))
        print("Lunches:", len(meals[2]))
        print("Afternoon Snack:", len(meals[3]))
        print("Dinners:", len(meals[4]))
        print("Total combinations:", total_combinations)
        if total_combinations > 100000:
            combinations = self.combinations(meals, NUMBER_OF_SAMPLES)
        else:
            combinations = self.combinations(meals, total_combinations)

        print("Final combinations:", len(combinations))

        for idx, combo in enumerate(combinations):
            meal_ids = [m.id for m in combo]
            nutrition = self.calculate_nutrition(combo)
            score = self.score_meal_plan(nutrition)
            temp_list.append(meal_ids)

            # Adjust score based on meal diversity
            penalty = sum(self.meal_counts[m.id] for m in combo) * 0.1  # Small penalty for repetition
            score -= penalty  # Reduce score if meals repeat

            entry = (score, idx, {
                "meals": [m.id for m in combo],
                "score": score,
                "nutrition": nutrition,
                "limits": {
                    "energy": self.user_energy_intake,
                    "protein": self.user_weight*0.83,
                    "carb": [0.45*nutrition.get('energy', 0)/4, 0.6*nutrition.get('energy', 0)/4],
                    "fat": [0.2*nutrition.get('energy', 0)/9, 0.35*nutrition.get('energy', 0)/9],
                    "fibre": 25,
                    "calcium": 1000,
                    "iron": 11,
                    "folate": 330,
                    "mea_q": 420,
                    "mea_s": 3,
                    "veg_q": 300,
                    "veg_s": 3,
                    "fru_q": 200,
                    "fru_s": 2,
                    "jui_s": 1,
                    "plp_q": 125,
                    "dai_q": [125, 250],
                    "dai_s": [1, 2],
                    "che_q": 25,
                    "che_s": 1,
                    "nns_q": 30,
                    "fis_q": 200,
                    "fis_s": 2,
                },
            })

            if all(self.meal_counts[m] < 5 for m in meal_ids):
                if len(top_plans) <= TOP_PLANS:
                    heapq.heappush(top_plans, entry)
                    self._update_meal_counts(meal_ids, increment=True)
                else:
                    if score > top_plans[0][0]:
                        removed = heapq.heappop(top_plans)
                        self._update_meal_counts(removed[2]["meals"], increment=False)
                        heapq.heappush(top_plans, entry)
                        self._update_meal_counts(meal_ids, increment=True)

        # for m in self.meal_counts:
        #     print(m, self.meal_counts[m])

        # breakfast = {}
        # lunch = {}
        # dinner = {}
        # for t in temp_list:
        #     if str(t[0]) in breakfast:
        #         breakfast[str(t[0])] += 1
        #     else:
        #         breakfast[str(t[0])] = 1

        #     if str(t[1]) in lunch:
        #         lunch[str(t[1])] += 1
        #     else:
        #         lunch[str(t[1])] = 1

        #     if str(t[2]) in dinner:
        #         dinner[str(t[2])] += 1
        #     else:
        #         dinner[str(t[2])] = 1

        # print()
        # for key, value in breakfast.items():
        #     print("br", key, value)
        # for key, value in lunch.items():
        #     print("lu", key, value)
        # for key, value in dinner.items():
        #     print("di", key, value)
        # quit()

        # Sort and return the final heap in descending order
        return sorted([plan[2] for plan in top_plans], key=lambda x: -x["score"])

class WeeklyMealPlanGenerator:
    # Configuration - could move to database model or settings
    NUTRITION_WEIGHTS = {
        "energy": 0.1,
        "protein": 0.08,
        "carb": 0.08,
        "fat": 0.08,
        "fibre": 0.06,
        "calcium": 0.1,
        "iron": 0.1,
        "folate": 0.1,
        "mea_q": 0.1,
        "mea_s": 0.1,
        "veg_q": 0.04,
        "veg_s": 0.02,
        "fru_q": 0.04,
        "fru_s": 0.2,
        "plp_q": 0.06,
        "dai_q": 0.02,
        "dai_s": 0.01,
        "che_q": 0.02,
        "che_s": 0.01,
        "nns_q": 0.06,
        "fis_q": 0.1,
        "fis_s": 0.1,
    }

    MEAL_TYPES = [
        "Breakfast",
        "Morning Snack",
        "Lunch",
        "Afternoon Snack",
        "Dinner"
    ]

    def __init__(self, results):
        self.results = results

    def calculate_nutrition(self, meals: Tuple[Meal]) -> Dict[str, float]:
        """Aggregate nutritional values and food group totals from meals"""

        # Initialize nutrition sums
        nutrition_totals = {
            "energy": sum(m['nutrition'].get('energy', 0) for m in meals),
            "protein": sum(m['nutrition'].get('protein', 0) for m in meals),
            "carb": sum(m['nutrition'].get('carb', 0) for m in meals),
            "fat": sum(m['nutrition'].get('fat', 0) for m in meals),
            "fibre": sum(m['nutrition'].get('fibre', 0) for m in meals),
            "calcium": sum(m['nutrition'].get('calcium', 0) for m in meals),
            "iron": sum(m['nutrition'].get('iron', 0) for m in meals),
            "folate": sum(m['nutrition'].get('folate', 0) for m in meals),
            "mea_q": sum(m['nutrition'].get('mea_q', 0) for m in meals),
            "mea_s": sum(m['nutrition'].get('mea_s', 0) for m in meals),
            "veg_s": sum(m['nutrition'].get('mea_q', 0) for m in meals),
            "veg_q": sum(m['nutrition'].get('veg_q', 0) for m in meals),
            "fru_s": sum(m['nutrition'].get('fru_s', 0) for m in meals),
            "fru_q": sum(m['nutrition'].get('fru_q', 0) for m in meals),
            "jui_s": sum(m['nutrition'].get('jui_s', 0) for m in meals),
            "jui_q": sum(m['nutrition'].get('jui_q', 0) for m in meals),
            "plp_s": sum(m['nutrition'].get('plp_s', 0) for m in meals),
            "plp_q": sum(m['nutrition'].get('plp_q', 0) for m in meals),
            "dai_s": sum(m['nutrition'].get('dai_s', 0) for m in meals),
            "dai_q": sum(m['nutrition'].get('dai_q', 0) for m in meals),
            "che_s": sum(m['nutrition'].get('che_s', 0) for m in meals),
            "che_q": sum(m['nutrition'].get('che_q', 0) for m in meals),
            "nns_s": sum(m['nutrition'].get('nns_s', 0) for m in meals),
            "nns_q": sum(m['nutrition'].get('nns_q', 0) for m in meals),
            "fis_q": sum(m['nutrition'].get('fis_q', 0) for m in meals),
            "fis_s": sum(m['nutrition'].get('fis_s', 0) for m in meals),
        }

        return nutrition_totals

    @staticmethod
    def _in_range(value: float, target: float, tolerance: float) -> bool:
        """Check if value is within target ± tolerance%"""
        return (target * (1 - tolerance)) <= value <= (target * (1 + tolerance))

    def score_meal_plan(self, nutrition: Dict[str, float]) -> float:
        """Modular scoring system with range checks"""
        score = 0.0

        # Meat quantity scoring
        meat_quantity_target = 420
        nutrition["mea_q_variable"] = 0
        nutrition["mea_q_prediction"] = nutrition.get("mea_q", 0)
        if self._in_range(nutrition.get("mea_q", 0), meat_quantity_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["mea_q"]
            nutrition["mea_q_variable"] = 10
        elif self._in_range(nutrition.get("mea_q", 0), meat_quantity_target, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["mea_q"]
            nutrition["mea_q_variable"] = 5

        # Meat serving scoring
        meat_serving_target = 3
        nutrition["mea_s_variable"] = 0
        nutrition["mea_s_prediction"] = nutrition.get("mea_s", 0)
        if self._in_range(nutrition.get("mea_s", 0), meat_serving_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["mea_s"]
            nutrition["mea_s_variable"] = 10
        elif self._in_range(nutrition.get("mea_s", 0), meat_serving_target, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["mea_s"]
            nutrition["mea_s_variable"] = 5

        # Fish quantity scoring
        fis_quantity_target = 200
        nutrition["fis_q_variable"] = 0
        nutrition["fis_q_prediction"] = nutrition.get("fis_q", 0)
        if self._in_range(nutrition.get("mea_s", 0), fis_quantity_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["fis_q"]
            nutrition["fis_q_variable"] = 10
        elif self._in_range(nutrition.get("fis_q", 0), fis_quantity_target, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["fis_q"]
            nutrition["fis_q_variable"] = 5

        # Fish serving scoring
        fis_serving_target = 2
        nutrition["fis_s_variable"] = 0
        nutrition["fis_s_prediction"] = nutrition.get("fis_s", 0)
        if self._in_range(nutrition.get("fis_s", 0), fis_serving_target, 0.05):
            score += 10 * self.NUTRITION_WEIGHTS["fis_s"]
            nutrition["fis_s_variable"] = 10
        elif self._in_range(nutrition.get("fis_s", 0), fis_serving_target, 0.10):
            score += 5 * self.NUTRITION_WEIGHTS["fis_s"]
            nutrition["fis_s_variable"] = 5

        return score

    def generate_combinations(self) -> Iterator[Tuple[Meal]]:
        """Generate meal combinations with smart sampling"""
        return combinations(self.results, 7)

    def process(self) -> List[Dict]:
        """Main processing pipeline"""

        top_plans = []
        combinations = self.generate_combinations()

        for idx, combo in enumerate(combinations):
            if idx == 1000:
                break

            nutrition = self.calculate_nutrition(combo)
            score = self.score_meal_plan(nutrition)

            entry = (score, idx, {
                "meals": [m['meals'] for m in combo],
                "score": score,
                "nutrition": nutrition,
            })

            heapq.heappush(top_plans, entry)

            if len(top_plans) > TOP_PLANS:
                heapq.heappop(top_plans)

        return sorted([plan[2] for plan in top_plans], key=lambda x: -x["score"])

class Command(BaseCommand):
    help = 'Generate personalized daily meal plans'

    def handle(self, *args, **kwargs):
        daily_generator = DailyMealPlanGenerator()
        daily_results = daily_generator.process()
        self.daily_dataframe_transform(daily_results)

        weekly_generator = WeeklyMealPlanGenerator(daily_results)
        weekly_results = weekly_generator.process()
        self.weekly_dataframe_transform(weekly_results)
        self.print_best_week(weekly_results[0])


    def print_best_week(self, result: List[Dict]):
        # Define day labels
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Define meal labels (optional)
        meal_labels = ["Breakfast", "Snack_1", "Lunch", "Snack_2", "Dinner"]

        # Create DataFrame
        df = pd.DataFrame(result['meals'], index=days_of_week, columns=meal_labels).T

        # Display DataFrame
        print(df)

    def weekly_dataframe_transform(self, results: List[Dict]):
        """Transform the results into a dataframe"""

        # Collect all meal plans in a list
        meal_plans_list = []

        #for idx, plan in enumerate(results, 1):
        print("------------------------------------------------------------------------------------------------------------------------------")
        # Iterate through top meal plans
        for plan in results:
            meal_plans_list.append({
                "Score": plan['score'],
                "Energy": f"{round(plan['nutrition']['energy'], 2)}",
                "Protein": f"{round(plan['nutrition']['protein'], 2)}",
                "Carbs": f"{round(plan['nutrition']['carb'], 2)}",
                "Fats": f"{round(plan['nutrition']['fat'], 2)}",
                "Fibre": f"{round(plan['nutrition']['fibre'], 2)}",
                "Iron": f"{round(plan['nutrition']['iron'], 2)}",
                "Calcium": f"{round(plan['nutrition']['calcium'], 2)}",
                "Folate": f"{round(plan['nutrition']['folate'], 2)}",
                "Veg_q": f"{plan['nutrition']['veg_q']}",
                "Veg_s": f"{plan['nutrition']['veg_s']}",
                "Fru_q": f"{plan['nutrition']['fru_q']}",
                "Fru_s": f"{plan['nutrition']['fru_s']}",
                "Jui_s": f"{plan['nutrition']['jui_s']}",
                "Pla_q": f"{plan['nutrition']['plp_q']}",
                "Dai_q": f"{plan['nutrition']['dai_q']}",
                "Dai_s": f"{plan['nutrition']['dai_s']}",
                "Che_q": f"{plan['nutrition']['che_q']}",
                "Che_s": f"{plan['nutrition']['che_s']}",
                "NnS_q": f"{plan['nutrition']['nns_q']}",
                "Mea_q": f"{int(plan['nutrition']['mea_q_prediction'])}",
                "Mea_s": f"{int(plan['nutrition']['mea_s_prediction'])}",
                "Fis_q": f"{int(plan['nutrition']['fis_q_prediction'])}",
                "Fis_s": f"{int(plan['nutrition']['fis_s_prediction'])}",
            })
        # Convert collected data into a DataFrame
        df = pd.DataFrame(meal_plans_list)

        # Print DataFrame
        print(df)

    def daily_dataframe_transform(self, results: List[Dict]):
        """Transform the results into a dataframe"""

        # Collect all meal plans in a list
        meal_plans_list = []

        #for idx, plan in enumerate(results, 1):
        print("------------------------------------------------------------------------------------------------------------------------------")
        # Iterate through top meal plans
        for plan in results:
            meal_plans_list.append({
                "Score": plan['score'],
                "Energy": f"{round(plan['nutrition']['energy_variable'], 2)}, {int(plan['nutrition']['energy_prediction'])}",
                "Protein": f"{round(plan['nutrition']['protein_variable'], 2)}, {int(plan['nutrition']['protein_prediction'])}",
                "Carbs": f"{round(plan['nutrition']['carb_variable'], 2)}, {int(plan['nutrition']['carb_prediction'])}",
                "Fats": f"{round(plan['nutrition']['fat_variable'], 2)}, {int(plan['nutrition']['fat_prediction'])}",
                "Fibre": f"{round(plan['nutrition']['fibre_variable'], 2)}, {int(plan['nutrition']['fibre_prediction'])}",
                "Iron": f"{round(plan['nutrition']['iron_variable'], 2)}, {int(plan['nutrition']['iron_prediction'])}",
                "Calcium": f"{round(plan['nutrition']['calcium_variable'], 2)}, {int(plan['nutrition']['calcium_prediction'])}",
                "Folate": f"{round(plan['nutrition']['folate_variable'], 2)}, {int(plan['nutrition']['folate_prediction'])}",
                "Veg_q": f"{plan['nutrition']['veg_q_variable']}, {int(plan['nutrition']['veg_q_prediction'])}",
                "Veg_s": f"{plan['nutrition']['veg_s_variable']}, {int(plan['nutrition']['veg_s_prediction'])}",
                "Fru_q": f"{plan['nutrition']['fru_q_variable']}, {int(plan['nutrition']['fru_q_prediction'])}",
                "Fru_s": f"{plan['nutrition']['fru_s_variable']}, {int(plan['nutrition']['fru_s_prediction'])}",
                "Jui_s": f"{plan['nutrition']['jui_s_variable']}, {int(plan['nutrition']['jui_s_prediction'])}",
                "Pla_q": f"{plan['nutrition']['plp_q_variable']}, {int(plan['nutrition']['plp_q_prediction'])}",
                "Dai_q": f"{plan['nutrition']['dai_q_variable']}, {int(plan['nutrition']['dai_q_prediction'])}",
                "Dai_s": f"{plan['nutrition']['dai_s_variable']}, {int(plan['nutrition']['dai_s_prediction'])}",
                "Che_q": f"{plan['nutrition']['che_q_variable']}, {int(plan['nutrition']['che_q_prediction'])}",
                "Che_s": f"{plan['nutrition']['che_s_variable']}, {int(plan['nutrition']['che_s_prediction'])}",
                "NnS_q": f"{plan['nutrition']['nns_q_variable']}, {int(plan['nutrition']['nns_q_prediction'])}",
                "Mea_q": f"{int(plan['nutrition']['mea_q_prediction'])}",
                "Mea_s": f"{int(plan['nutrition']['mea_s_prediction'])}",
                "Fis_q": f"{int(plan['nutrition']['fis_q_prediction'])}",
                "Fis_s": f"{int(plan['nutrition']['fis_s_prediction'])}",
            })
        # Convert collected data into a DataFrame
        df = pd.DataFrame(meal_plans_list)

        # Print DataFrame
        print(df)
