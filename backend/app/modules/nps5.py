from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
from ..models import Dish, Meal, UserProfile, NP, NPItem
#from .models import Meal, Dish
from django.contrib.auth.models import User
import itertools
from itertools import product
import pandas as pd
from random import sample
import heapq
from typing import Dict, List, Tuple, Iterator
from collections import defaultdict
from django.db.models import Q
from itertools import combinations
import random

N_MEAL_PLANS = 10000  # Reduced from 20,000 for initial testing
TOP_PLANS = 20
NUTRIENT_TOLERANCE = 0.1  # 10% tolerance for most nutrients
SAMPLE_SIZE = 10
NUMBER_OF_SAMPLES = 100000

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


def _update_meal_counts(meal_counts, meal_ids: List[int], increment: bool):
    """NEW: Properly handle meal count updates"""
    delta = 1 if increment else -1
    for i, m in enumerate(meal_ids):
        #if i in [0, 2, 4]:  # Only track main meals
        meal_counts[m] += delta


def _in_range(value: float, target: float, tolerance: float) -> bool:
    """Check if value is within target ± tolerance%"""
    return (target * (1 - tolerance)) <= value <= (target * (1 + tolerance))


def score_meal_plan(user_energy_intake, user_weight, nutrition: Dict[str, float]) -> float:
    """Modular scoring system with range checks"""
    score = 0.0

    # Energy scoring
    energy_target = user_energy_intake
    nutrition["energy_variable"] = 0
    nutrition["energy_prediction"] = nutrition.get("energy", 0)
    if _in_range(nutrition.get("energy", 0), energy_target, 0.05):
        score += 10 * NUTRITION_WEIGHTS["energy"]
        nutrition["energy_variable"] = 10
    elif _in_range(nutrition.get("energy", 0), energy_target, 0.10):
        score += 5 * NUTRITION_WEIGHTS["energy"]
        nutrition["energy_variable"] = 5

    # Protein scoring
    protein_target = user_weight * 0.83
    nutrition["protein_variable"] = 0
    nutrition["protein_prediction"] = nutrition.get("protein", 0)
    if _in_range(nutrition.get("protein", 0), protein_target, 0.05):
        score += 10 * NUTRITION_WEIGHTS["protein"]
        nutrition["protein_variable"] = 10
    elif _in_range(nutrition.get("protein", 0), protein_target, 0.10):
        score += 5 * NUTRITION_WEIGHTS["protein"]
        nutrition["protein_variable"] = 5

    # Carb scoring
    nutrition["carb_variable"] = 0
    nutrition["carb_prediction"] = nutrition.get("carb", 0)
    if 0.45*user_energy_intake/4 <= nutrition.get("carb", 0) <= 0.6*user_energy_intake/4:
        score += 10 * NUTRITION_WEIGHTS["carb"]
        nutrition["carb_variable"] = 10

    # Fats scoring
    nutrition["fat_variable"] = 0
    nutrition["fat_prediction"] = nutrition.get("fat", 0)
    if 0.2*user_energy_intake/9 <= nutrition.get("fat", 0) <= 0.35*user_energy_intake/9:
        score += 10 * NUTRITION_WEIGHTS["fat"]
        nutrition["fat_variable"] = 10

    # Fibre scoring
    nutrition["fibre_variable"] = 0
    nutrition["fibre_prediction"] = nutrition.get("fibre", 0)
    if nutrition.get("fibre", 0) > 22.5:
        score += 10 * NUTRITION_WEIGHTS["fibre"]
        nutrition["fibre_variable"] = 10
    elif nutrition.get("fibre", 0) > 20:
        score += 5 * NUTRITION_WEIGHTS["fibre"]
        nutrition["fibre_variable"] = 5

    # Calcuim scoring
    calcium_target = 1000
    nutrition["calcium_variable"] = 0
    nutrition["calcium_prediction"] = nutrition.get("calcium", 0)
    if _in_range(nutrition.get("calcium", 0), calcium_target, 0.05):
        score += 10 * NUTRITION_WEIGHTS["calcium"]
        nutrition["calcium_variable"] = 10
    elif _in_range(nutrition.get("calcium", 0), calcium_target, 0.10):
        score += 5 * NUTRITION_WEIGHTS["calcium"]
        nutrition["calcium_variable"] = 5

    # Iron scoring
    # if use.sex == 'Male':
    #     iron_target = 11
    # elif user.sex == 'Female':
    #     iron_target = 17
    iron_target = 11
    nutrition["iron_variable"] = 0
    nutrition["iron_prediction"] = nutrition.get("iron", 0)
    if _in_range(nutrition.get("iron", 0), iron_target, 0.05):
        score += 10 * NUTRITION_WEIGHTS["iron"]
        nutrition["iron_variable"] = 10
    elif _in_range(nutrition.get("iron", 0), iron_target, 0.10):
        score += 5 * NUTRITION_WEIGHTS["iron"]
        nutrition["iron_variable"] = 5

    # Folate scoring
    folate_target = 330
    nutrition["folate_variable"] = 0
    nutrition["folate_prediction"] = nutrition.get("folate", 0)
    if _in_range(nutrition.get("folate", 0), folate_target, 0.05):
        score += 10 * NUTRITION_WEIGHTS["folate"]
        nutrition["folate_variable"] = 10
    elif _in_range(nutrition.get("folate", 0), folate_target, 0.10):
        score += 5 * NUTRITION_WEIGHTS["folate"]
        nutrition["folate_variable"] = 5

    # Vegetable quantity scoring
    nutrition["veg_q_variable"] = 0
    nutrition["veg_q_prediction"] = nutrition.get("veg_q", 0)
    if nutrition.get("veg_q", 0) > 270:
        score += 10 * NUTRITION_WEIGHTS["veg_q"]
        nutrition["veg_q_variable"] = 10
    elif nutrition.get("veg_q", 0) > 240:
        score += 5 * NUTRITION_WEIGHTS["veg_q"]
        nutrition["veg_q_variable"] = 5

    # Vegetable serving scoring
    nutrition["veg_s_variable"] = 0
    nutrition["veg_s_prediction"] = nutrition.get("veg_s", 0)
    if nutrition.get("veg_s", 0) > 2:
        score += 10 * NUTRITION_WEIGHTS["veg_s"]
        nutrition["veg_s_variable"] = 10
    elif nutrition.get("veg_s", 0) > 1:
        score += 5 * NUTRITION_WEIGHTS["veg_s"]
        nutrition["veg_s_variable"] = 5

    # Fruit quantity scoring
    fruit_quantity_variable = 0
    fruit_quantity_target = 200
    nutrition["fru_q_variable"] = 0
    nutrition["fru_q_prediction"] = nutrition.get("fru_q", 0)
    if _in_range(nutrition.get("fru_q", 0), fruit_quantity_target, 0.05):
        score += 10 * NUTRITION_WEIGHTS["fru_q"]
        nutrition["fru_q_variable"] = 10
    elif _in_range(nutrition.get("fru_q", 0), fruit_quantity_target, 0.1):
        score += 5 * NUTRITION_WEIGHTS["fru_q"]
        nutrition["fru_q_variable"] = 5

    # Fruit serving scoring
    fruit_serving_target = 2
    nutrition["fru_s_variable"] = 0
    nutrition["fru_s_prediction"] = nutrition.get("fru_s", 0)
    if nutrition.get("fru_s", 0) == fruit_serving_target:
        score += 10 * NUTRITION_WEIGHTS["fru_s"]
        nutrition["fru_s_variable"] = 10
    elif fruit_serving_target-1 <= nutrition.get("fru_s", 0) <= fruit_serving_target+1:
        score += 5 * NUTRITION_WEIGHTS["fru_s"]
        nutrition["fru_s_variable"] = 5

    # Juice serving scoring
    juice_serving_target = 1
    nutrition["jui_s_variable"] = 0
    nutrition["jui_s_prediction"] = nutrition.get("jui_s", 0)
    if nutrition.get("Jui_s", 0) > juice_serving_target:
        score += -1 * NUTRITION_WEIGHTS["jui_s"]
        nutrition["jui_s_variable"] = -1

    # Plant protein quantity scoring
    nutrition["plp_q_variable"] = 0
    nutrition["plp_q_prediction"] = nutrition.get("plp_q", 0)
    if nutrition.get("plp_q", 0) > 112.5:
        score += 10 * NUTRITION_WEIGHTS["plp_q"]
        nutrition["plp_q_variable"] = 10
    elif nutrition.get("plp_q", 0) > 100:
        score += 5 * NUTRITION_WEIGHTS["plp_q"]
        nutrition["plp_q_variable"] = 5

    # Dairy quantity scoring
    nutrition["dai_q_variable"] = 0
    nutrition["dai_q_prediction"] = nutrition.get("dai_q", 0)
    if 125 <= nutrition.get("dai_q", 0) <= 250:
        score += 10 * NUTRITION_WEIGHTS["dai_q"]
        nutrition["dai_q_variable"] = 10

    # Dairy serving scoring
    nutrition["dai_s_variable"] = 0
    nutrition["dai_s_prediction"] = nutrition.get("dai_s", 0)
    if 1 <= nutrition.get("dai_s", 0) <= 2:
        score += 10 * NUTRITION_WEIGHTS["dai_s"]
        nutrition["dai_s_variable"] = 10

    # Cheese quantity scoring
    cheese_quantity_ratget = 25
    nutrition["che_q_variable"] = 0
    nutrition["che_q_prediction"] = nutrition.get("che_q", 0)
    if _in_range(nutrition.get("che_q", 0), cheese_quantity_ratget, 0.05):
        score += 10 * NUTRITION_WEIGHTS["che_q"]
        nutrition["che_q_variable"] = 10
    elif _in_range(nutrition.get("che_q", 0), cheese_quantity_ratget, 0.10):
        score += 5 * NUTRITION_WEIGHTS["che_q"]
        nutrition["che_q_variable"] = 5

    # Cheese serving scoring
    cheese_serving_ratget = 1
    nutrition["che_s_variable"] = 0
    nutrition["che_s_prediction"] = nutrition.get("che_s", 0)
    if nutrition.get("che_s", 0) == 1:
        score += 10 * NUTRITION_WEIGHTS["che_s"]
        nutrition["che_s_variable"] = 10

    # Nuts and seeds quantity scoring
    nuts_and_seeds_quantity_target = 30
    nutrition["nns_q_variable"] = 0
    nutrition["nns_q_prediction"] = nutrition.get("nns_q", 0)
    if _in_range(nutrition.get("nns_q", 0), nuts_and_seeds_quantity_target, 0.05):
        score += 10 * NUTRITION_WEIGHTS["nns_q"]
        nutrition["nns_q_variable"] = 10
    elif _in_range(nutrition.get("nns_q", 0), nuts_and_seeds_quantity_target, 0.10):
        score += 5 * NUTRITION_WEIGHTS["nns_q"]
        nutrition["nns_q_variable"] = 5

    # Add meat to nutrition dictionary
    nutrition["mea_q_prediction"] = nutrition.get("mea_q", 0)
    nutrition["mea_s_prediction"] = nutrition.get("mea_s", 0)

    # Add fish to nutrition dictionary
    nutrition["fis_q_prediction"] = nutrition.get("fis_q", 0)
    nutrition["fis_s_prediction"] = nutrition.get("fis_s", 0)

    return score


def calculate_nutrition(meals: Tuple[Meal]) -> Dict[str, float]:
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


def _combinations(sets, num_samples):
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


def get_five_meals(meals):
    """Devide meals based on meal type"""
    meals = [
        meals.filter(Type="Breakfast"),
        meals.filter(Type="Snack"),
        meals.filter(Type="Lunch"),
        meals.filter(Type="Snack"),
        meals.filter(Type="Dinner")
    ]
    return meals


def filter_meals_preferences_and_allergies(meals, preferences, allergies):
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


def load_meals(user_country, user_preferences, user_allergies):
    """Load all meals based on user's restrictions"""
    filters = {
        "Country__in": user_country
    }
    queryset = Meal.objects.filter().only(
            'id', 'Total_Energy', 'Total_Protein',
            'Total_Fat', 'Total_Carbs', 'Total_Fibre', 'Total_Calcium',
            'Total_Iron', 'Total_Folate', 'Food_Groups_Counter',
    )
    queryset = queryset.filter(Country__in=user_country)
    queryset = filter_meals_preferences_and_allergies(queryset, user_preferences, user_allergies)
    return (queryset)


def daily_process(user_country, user_preferences, user_allergies, user_energy_intake, user_weight, meal_counts) -> List[Dict]:
    """Main processing pipeline"""
    top_plans = []
    temp_list = []
    meals = load_meals(user_country, user_preferences, user_allergies)
    meals = get_five_meals(meals)

    total_combinations = len(meals[0])*len(meals[1])*len(meals[2])*len(meals[3])*len(meals[4])
    print("Breakfasts:", len(meals[0]))
    print("Morning Snacks:", len(meals[1]))
    print("Lunches:", len(meals[2]))
    print("Afternoon Snack:", len(meals[3]))
    print("Dinners:", len(meals[4]))
    print("Total combinations:", total_combinations)

    if total_combinations > 100000:
        combinations = _combinations(meals, NUMBER_OF_SAMPLES)
    else:
        combinations = _combinations(meals, total_combinations)

    print("Final combinations:", len(combinations))

    for idx, combo in enumerate(combinations):
        meal_ids = [m.id for m in combo]
        nutrition = calculate_nutrition(combo)
        score = score_meal_plan(user_energy_intake, user_weight, nutrition)
        temp_list.append(meal_ids)

        # Adjust score based on meal diversity
        penalty = sum(meal_counts[m.id] for m in combo) * 0.1  # Small penalty for repetition
        score -= penalty  # Reduce score if meals repeat

        entry = (score, idx, {
            "meals": [m.id for m in combo],
            "score": score,
            "nutrition": nutrition,
            "limits": {
                "energy": user_energy_intake,
                "protein": user_weight*0.83,
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

        if all(meal_counts[m] < 5 for m in meal_ids):
            if len(top_plans) <= TOP_PLANS:
                heapq.heappush(top_plans, entry)
                _update_meal_counts(meal_counts, meal_ids, increment=True)
            else:
                if score > top_plans[0][0]:
                    removed = heapq.heappop(top_plans)
                    _update_meal_counts(meal_counts, removed[2]["meals"], increment=False)
                    heapq.heappush(top_plans, entry)
                    _update_meal_counts(meal_counts, meal_ids, increment=True)

    return sorted([plan[2] for plan in top_plans], key=lambda x: -x["score"])


def daily_dataframe_transform(results: List[Dict]):
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


def generate_combinations(results) -> Iterator[Tuple[Meal]]:
        """Generate meal combinations with smart sampling"""
        return combinations(results, 7)


def weekly_score_meal_plan(nutrition: Dict[str, float]) -> float:
    """Modular scoring system with range checks"""
    score = 0.0

    # Meat quantity scoring
    meat_quantity_target = 420
    nutrition["mea_q_variable"] = 0
    nutrition["mea_q_prediction"] = nutrition.get("mea_q", 0)
    if _in_range(nutrition.get("mea_q", 0), meat_quantity_target, 0.05):
        score += 10 * NUTRITION_WEIGHTS["mea_q"]
        nutrition["mea_q_variable"] = 10
    elif _in_range(nutrition.get("mea_q", 0), meat_quantity_target, 0.10):
        score += 5 * NUTRITION_WEIGHTS["mea_q"]
        nutrition["mea_q_variable"] = 5

    # Meat serving scoring
    meat_serving_target = 3
    nutrition["mea_s_variable"] = 0
    nutrition["mea_s_prediction"] = nutrition.get("mea_s", 0)
    if _in_range(nutrition.get("mea_s", 0), meat_serving_target, 0.05):
        score += 10 * NUTRITION_WEIGHTS["mea_s"]
        nutrition["mea_s_variable"] = 10
    elif _in_range(nutrition.get("mea_s", 0), meat_serving_target, 0.10):
        score += 5 * NUTRITION_WEIGHTS["mea_s"]
        nutrition["mea_s_variable"] = 5

    # Fish quantity scoring
    fis_quantity_target = 200
    nutrition["fis_q_variable"] = 0
    nutrition["fis_q_prediction"] = nutrition.get("fis_q", 0)
    if _in_range(nutrition.get("mea_s", 0), fis_quantity_target, 0.05):
        score += 10 * NUTRITION_WEIGHTS["fis_q"]
        nutrition["fis_q_variable"] = 10
    elif _in_range(nutrition.get("fis_q", 0), fis_quantity_target, 0.10):
        score += 5 * NUTRITION_WEIGHTS["fis_q"]
        nutrition["fis_q_variable"] = 5

    # Fish serving scoring
    fis_serving_target = 2
    nutrition["fis_s_variable"] = 0
    nutrition["fis_s_prediction"] = nutrition.get("fis_s", 0)
    if _in_range(nutrition.get("fis_s", 0), fis_serving_target, 0.05):
        score += 10 * NUTRITION_WEIGHTS["fis_s"]
        nutrition["fis_s_variable"] = 10
    elif _in_range(nutrition.get("fis_s", 0), fis_serving_target, 0.10):
        score += 5 * NUTRITION_WEIGHTS["fis_s"]
        nutrition["fis_s_variable"] = 5

    return score


def weekly_calculate_nutrition(meals: Tuple[Meal]) -> Dict[str, float]:
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


def weekly_process(results) -> List[Dict]:
    """Main processing pipeline"""
    top_plans = []
    combinations = generate_combinations(results)

    for idx, combo in enumerate(combinations):
        if idx == 1000:
            break

        nutrition = weekly_calculate_nutrition(combo)
        score = weekly_score_meal_plan(nutrition)

        entry = (score, idx, {
            "meals": [m['meals'] for m in combo],
            "score": score,
            "nutrition": nutrition,
        })

        heapq.heappush(top_plans, entry)

        if len(top_plans) > TOP_PLANS:
            heapq.heappop(top_plans)

    return sorted([plan[2] for plan in top_plans], key=lambda x: -x["score"])


def print_best_week(result: List[Dict]):
    # Define day labels
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Define meal labels (optional)
    meal_labels = ["Breakfast", "Snack_1", "Lunch", "Snack_2", "Dinner"]

    # Create DataFrame
    df = pd.DataFrame(result['meals'], index=days_of_week, columns=meal_labels).T

    # Display DataFrame
    print(df)


def weekly_dataframe_transform(results: List[Dict]):
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


@api_view(['GET'])
def create_np(request, user_id, week_monday, week_sunday):
    # Check the request method.
    if request.method != 'GET':
        return JsonResponse({"error": "No GET request."}, status=400)
    # Check if th Django User exists for the paricullar id.
    if User.objects.filter(id=user_id).exists():
        # Given the user id retrieve the corresponding user from the Djando User model.
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({"error": f"No User found for id: {user_id}"}, status=400)
    # Check if the UserProfile user exists.
    if UserProfile.objects.get(User=user):
        # Having the Django User we retrieve the corresponding user from the UserProfile model.
        user_profile = UserProfile.objects.get(User=user)
    else:
        return JsonResponse({"error", f"No UserProfile user for User: {user.id}"}, status=400)

    user_weight = 80
    user_energy_intake = 2200
    user_country = ["Ireland"]
    user_preferences = "vegan"
    user_allergies = "milk_allergy"
    meal_counts = defaultdict(int)  # Track meal occurrences in heap

    daily_results = daily_process(user_country, user_preferences, user_allergies, user_energy_intake, user_weight, meal_counts)
    daily_dataframe_transform(daily_results)

    weekly_results = weekly_process(daily_results)
    weekly_dataframe_transform(weekly_results)
    print_best_week(weekly_results[0])

    return JsonResponse({'message': f"NP created."}, status=200)




def calculate_characteristics(sex, age, height, weight, pal, target_weight, goal, target_goal):
    # Calculate user's BMI based on user's weight and height.
    bmi = weight / ((height/100) ** 2)

     # Calculate BMR
    # Males (aged 18–30): BMR (in kcal) = 14.4 × Body Mass (in kg) + 3.13 × Height (in cm) + 113
    # Females (aged 18–30): BMR (in kcal) = 10.4 × Body Mass (in kg) + 6.15 × Height (in cm) – 282
    # Calculation of bmr based on sex and age.
    if sex in "Male, male":
        if 0 < age <= 3:
            bmr = 28.2 * weight + 8.59 * height - 371
        elif 3 < age <= 10:
            bmr = 15.1 * weight + 7.42 * height + 306
        elif 10 < age <= 18:
            bmr = 15.6 * weight + 2.66 * height + 299
        elif 18 < age <= 30:
            bmr = 14.4 * weight + 3.13 * height + 113
        elif 30 < age <= 60:
            bmr = 11.4 * weight + 5.41 * height - 137
        else:
            bmr = 11.4 * weight + 5.41 * height - 256
    elif sex in "Female, female":
        if 0 < age <= 3:
            bmr = 30.4 * weight + 7.03 * height - 287
        elif 3 < age <= 10:
            bmr = 15.9 * weight + 2.10 * height + 349
        elif 10 < age <= 18:
            bmr = 9.4 * weight + 2.49 * height + 462
        elif 18 < age <= 30:
            bmr = 10.4 * weight + 6.15 * height - 282
        elif 30 < age <= 60:
            bmr = 8.18 * weight + 5.02 * height - 116
        else:
            bmr = 8.52 * weight + 4.21 * height + 107
    else:
        return None

    # Calculate user's energy intake based user's target_weight (that means how mutch kgs
    # the user wants to gain or lose), and target_goal (how fast to achieve the target_weight.
    # There are 2 gears, Normal which is +-500 kcal and Intence which is +-750 kcal).
    if target_weight < weight:
        if target_goal == "normal":
            energy_intake = bmr * pal - 500
        elif target_goal == "fast":
            energy_intake = bmr * pal - 750
        else:
            return None
    elif target_weight == weight:
        energy_intake = bmr * pal
    elif target_weight > weight:
        if target_goal == "normal":
            energy_intake = bmr * pal + 500
        elif target_goal == "fast":
            energy_intake = bmr * pal + 750
        else:
            return None
    else:
        return None

    return bmi, bmr, energy_intake


def generate_random_combinations(sets, num_samples):
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

def filter_meals_seasonality(meals):
    # Check for seasonality. For this to be done get the current month, declare 4 lists one for
    # each seasson with each list contaning the number of moths that corresponds to each
    # seasson. Run four (4) if-else to find in which season we currently are.
    current_month = int(str(date.today()).split('-')[1])  # Get current moth.

    winter = [12, 1, 2]  # List for winter seasson
    spring = [3, 4, 5]  # List for spring seasson
    summer = [6, 7, 8]  # List for summer seasson
    autumn = [9, 10, 11]  # List for autumn seasson

    if current_month in winter:  # Check if current month is in winter seasson.
        # Filter the meals table based on the meals that are for the winter seasson.
        meals = meals.filter(Winter="Y")
        return meals
    elif current_month in spring:  # Check if current month is in spring seasson.
        # Filter the meals table based on the meals that are for the spring seasson.
        meals = meals.filter(Spring="Y")
        return meals
    elif current_month in summer:  # Check if current month is in summer seasson.
        # Filter the meals table based on the meals that are for the summer seasson.
        meals = meals.filter(Summer="Y")
        return meals
    elif current_month in autumn:  # Check if current month is in autumn seasson.
        # Filter the meals table based on the meals that are for the autumn seasson.
        meals = meals.filter(Autumn="Y")
        return meals
    else:  # Check if there is an error while fingurring which season we are.
        print("We checked for all four seasons and no season found.")
        return None

def filter_meals_type(meals):
    # Create corresponding lists for every meal type.
    # From the filtered meals based on the seasson that are retrieved above we now
    # classifide them based on their meal type. For this we create 5 corresponding
    # lists one for each meal type and we filter the meals table based on each meal type.
    # Check if any of these lists are empty. If yes that means an error. Combine the
    # fife lists into one. Use the itertools function to create all possible combinations
    # of the five meal type lists.
    # PS. The number of daily meals will change danimacally from the user. User's will choose
    # if they want 3, 4, or 5 meals per day.
    # Implement this choice here in the backend later.

    # Filter the meals table and keep only the breakfasts.
    breakfasts = meals.filter(Type="Breakfast")
    # Filter the meals table and keep only the morning snacks.
    morning_snacks = meals.filter(Type="Snack")
    # Filter the meals table and keep only the lunches.
    lunches = meals.filter(Type="Lunch")
    # Filter the meals table and keep only the afternoon snacks.
    afternoon_snacks = meals.filter(Type="Snack")
    # Filter the meals table and keep only the dinners.
    dinners = meals.filter(Type="Dinner")

    return breakfasts, morning_snacks, lunches, afternoon_snacks, dinners


def sum_nps_characteristics(res, user_id):
    """
    Function that sums up the nutrients and count the amound of food groups in NP level.
    """

    np_info_dict = {}  # Create a dictionary to hold the data for all posible meal combinations
    food_group_dict = { # experts
        # exclude all foods from CoFID food group codes MI and MIG (processed meats)
        "Meat": ["MA", "MAA", "MAC", "MAE", "MAG", "MAI", "MC", "MCA", "MCC", "MCE", "MCG", "MI",
                 "MCK", "MCM", "MCO", "ME", "MEA", "MEC", "MEE", "MG", "MBG", "MI", "MIG", "MR"],
        "Plant_protein": ["DB"],
        "Vegetables": ["DF", "DG", "DI", "DR"],
        # with no more than 1 serving per day from FC
        "Fruit": ["F", "FA", "FC"],
        # with no more than 1 serving of BL per day
        "Dairy": ["BA", "BC", "BL", "BN"],
        "Nuts_and_seeds": ["G", "GA"],
        # with at least 1 serving per week from JC
        "Fish": ["J", "JA", "JC", "JK", "JM", "JR"],
    }

    food_group_dict = {
        # kyriakos.
        "Fruit": ["FA", "FC"],
        "Raw_Vegetables": ["DG", "DI"],
        "Cooked_Vegetables": ["DR"],
        "Frandveg": ["FA", "FC", "DG", "DI", "DR"],
        "Eggs": ["C", "CA", "CD"],
        "Fruit_Salad": [],  # No explicit code for fruit salad in your list
        "Processed_Meat": ["MBG", "MI", "MIG"],
        "Red_Meat": ["MAC", "MAE", "MAG", "MAI", "MEE"],
        "White_Meat": ["MC"],
        "Chicken": ["MCA"],
        "Turkey": ["MCO"],
        "Rabbit": ["MEC"],
        "Pulses": ["DB", "DF"],
        "Chickpeas": [],  # Not explicitly mentioned
        "Lentils": ["DB"],
        "White_Red_Beans": [],  # Not explicitly mentioned
        "Other_Legumes": ["DB", "DF"],
        "Tubers": ["DA", "DAE", "DAM", "DAP", "DAR"],
        "Rice": ["AC"],
        "Pasta": ["AD"],
        "Fish": ["JA", "JC", "JK", "JM", "JR"],

        # Experts.
        # exclude all foods from CoFID food group codes MI and MIG (processed meats)
        "Meat": ["MA", "MAA", "MAC", "MAE", "MAG", "MAI", "MC", "MCA", "MCC", "MCE", "MCG", "MI",
                 "MCK", "MCM", "MCO", "ME", "MEA", "MEC", "MEE", "MG", "MBG", "MI", "MIG", "MR"],
        "Plant_protein": ["DB"],
        "Vegetables": ["DF", "DG", "DI", "DR"],
        # with no more than 1 serving per day from FC
        "Fruit": ["F", "FA", "FC"],
        # with no more than 1 serving of BL per day
        "Dairy": ["BA", "BC", "BL", "BN"],
        "Nuts_and_seeds": ["G", "GA"],
        # with at least 1 serving per week from JC
        "Fish": ["J", "JA", "JC", "JK", "JM", "JR"],
    }

    nutrition_list = ["Total_Energy", "Total_Protein", "Total_Fat", "Total_Carbs", "Total_Fibre", "Total_Saturated_fat", "Total_Omega3", "Total_Salt",
                      "Total_Calcium", "Total_Iron", "Total_Zinc", "Total_Folate", "Total_Vitamin_a", "Total_Vitamin_c", "Total_Vitamin_b12"]
    dish_list = ["Dish_1", "Dish_2", "Dish_3", "Dish_4",
                 "Dish_5", "Dish_6", "Dish_7", "Dish_8"]

def score_nps(energy_intake, weight, np_info_dict):
    '''
    The score_NPs function is responsible for providing a total score of a meal plan.
    It checks how good a meal is based on its energy, protein and fats and returns a
    score (a number).
    '''

    # Kyriako's approach.
    award_value = 0
    penalty_value = 50
    strong_penalty_value = 100
    fat_t1 = energy_intake*0.20
    fat_t2 = energy_intake*0.35
    protein_t1 = energy_intake*0.15
    protein_t2 = energy_intake*0.20
    carbs_t1 = 0.45
    carbs_t2 = 0.60

    # Experts approach.
    # Macronutrients
    protein_score = 0.83 * weight # 0.83 g/kg/d
    carbohydrate_score = [0.45*energy_intake/4, 0.6*energy_intake/4] # 45-60 %kcal / 4 kcal per gram of carb.
    fat_score = [0.2*energy_intake/9, 0.35*energy_intake/9] # 20-35 %kcal / 9 kcal per gram of fat.
    fibre_score = 25 # 25 g per day is the target (if that causes problems for the algorithm, aim for 20 g per day)

    # Micronutrients
    calcium_score = 1000 # 1,000 mg per day
    iron_score = 11 # 11 mg per day for males; 17 mg per day for females
    folate_score = 330 # 330 mcg per day

    weights = {
        "calories": 0.4,  # Most important
        "protein": 0.2,
        "carbs": 0.2,
        "fat": 0.1,
        "fibre": 0.05,
        "calcium": 0.005,
        "iron": 0.005,
        "folate": 0.005
    }

    for np in np_info_dict:
        # Kyriakos approach.
        # how good is that NP regarding calories
        #caloric_distance[i] = abs(kcal - energy_intake)
        caloric_distance = abs(np_info_dict[np]["Total_Energy"] - energy_intake)

        # how good is the NP regarding fats
        if np_info_dict[np]["Total_Fat"] * 9 >= fat_t1 and np_info_dict[np]["Total_Fat"] * 9 <= fat_t2:
            fat_distance = award_value
        else:
            fat_distance = penalty_value

        # how good is the NP regarding protein
        if np_info_dict[np]["Total_Protein"] * 4 >= protein_t1 and np_info_dict[np]["Total_Protein"] * 4 <= protein_t2:
            protein_distance = award_value
        else:
            protein_distance = penalty_value

        # how good is the NP regarding carbs
        if np_info_dict[np]["Total_Carbs"] * 4 >= carbs_t1 and np_info_dict[np]["Total_Carbs"] * 4 <= carbs_t2:
            carbs_distance = award_value
        else:
            carbs_distance = penalty_value

        # how good is the NP regarding carbs
        if np_info_dict[np]["Total_Carbs"] * 4 >= carbs_t1 and np_info_dict[np]["Total_Carbs"] * 4 <= carbs_t2:
            carbs_distance = award_value
        else:
            carbs_distance = penalty_value

        # how good is the NP regarding fruits and vegetables
        def get_frandveg(food_groups_dict):
            list_of_fruits_and_vegetables = ["F", "FA", "FC", "D", "DA", "DAE", "DAM", "DAP", "DAR", "DB", "DF", "DG", "DI", "DR"]
            number_of_fruits_and_vegetables = 0
            for group in food_groups_dict["Group"]:
                if group in list_of_fruits_and_vegetables:
                    number_of_fruits_and_vegetables += food_groups_dict["Group"][group]
            return number_of_fruits_and_vegetables
        frandveg = get_frandveg(np_info_dict[np])
        if frandveg >= 5 and frandveg <= 10:
            frandveg_distance = award_value
        else:
            frandveg_distance = strong_penalty_value

        appropriateness_distance = caloric_distance + fat_distance + protein_distance + carbs_distance + frandveg_distance

        # # Experts approach
        # # Quality of np regarding macronutrients.
        # # How good is that NP regarding calories
        # caloric_distance = abs(np_info_dict[np]["Total_Energy"] - energy_intake) / energy_intake
        # # How good is the NP regarding protein
        # protein_distance = abs(np_info_dict[np]["Total_Protein"] - protein_score) / protein_score
        # # How good is the NP regarding carbs
        # carbs_distance = 1
        # # If total carbs are between the limits.
        # if carbohydrate_score[0] <= np_info_dict[np]["Total_Carbs"] <= carbohydrate_score[1]:
        #     carbs_distance = 0
        # else:
        #     # If total carb is less than the lowe limit.
        #     if np_info_dict[np]["Total_Carbs"] < carbohydrate_score[0]:
        #         carbs_distance = abs(np_info_dict[np]["Total_Carbs"] - carbohydrate_score[0]) / carbohydrate_score[0]
        #     # If total carb is more than the upper limit.
        #     else:
        #         carbs_distance = abs(np_info_dict[np]["Total_Carbs"] - carbohydrate_score[1]) / carbohydrate_score[1]
        # # How good is the NP regarding fats
        # fat_distance = 1
        # # If total fat are between the limits.
        # if fat_score[0] <= np_info_dict[np]["Total_Fat"] <= fat_score[1]:
        #     fat_distance = 0
        # else:
        #     # If total fat is less than the lowe limit.
        #     if np_info_dict[np]["Total_Fat"] < fat_score[0]:
        #         fat_distance = abs(np_info_dict[np]["Total_Fat"] - fat_score[0]) / fat_score[0]
        #     # If total fat is less than the lowe limit.
        #     else:
        #         fat_distance = abs(np_info_dict[np]["Total_Fat"] - fat_score[1]) / fat_score[1]
        # # How good is the NP regarding fibres.
        # fibre_distance = abs(np_info_dict[np]["Total_Fibre"] - fibre_score) / fibre_score

        # # Quality of np regarding micronutrients.
        # # How good is the NP regarding calcium.
        # calcium_distance = abs(np_info_dict[np]["Total_Calcium"] - calcium_score) / calcium_score
        # # How good is the NP regarding iron.
        # iron_distance = abs(np_info_dict[np]["Total_Iron"] - iron_score) / iron_score
        # # How good is the NP regarding folate.
        # folate_distance = abs(np_info_dict[np]["Total_Folate"] - folate_score) / folate_score
        # #macronutrients_distance = protein_distance + carbs_distance + fat_distance + fibre_distance
        # #micronutrients_distance = calcium_distance + iron_distance + folate_distance
        # #appropriateness_distance = caloric_distance + macronutrients_distance + micronutrients_distance
        # appropriateness_distance = (
        #     weights["calories"] * caloric_distance +
        #     weights["protein"] * protein_distance +
        #     weights["carbs"] * carbs_distance +
        #     weights["fat"] * fat_distance +
        #     weights["fibre"] * fibre_distance +
        #     weights["calcium"] * calcium_distance +
        #     weights["iron"] * iron_distance +
        #     weights["folate"] * folate_distance
        # )

        # # print("caloric_distance", caloric_distance)
        # # print("protein_distance", protein_distance)
        # # print("carbs_distance", carbs_distance)
        # # print("fat_distance", fat_distance)
        # # print("fibre_distance", fibre_distance)
        # # print("calcium_distance", calcium_distance)
        # # print("iron_distance", iron_distance)
        # # print("folate_distance", folate_distance)
        # # print("Macronutrients distance:", macronutrients_distance)
        # # print("Micronutrients distance:", micronutrients_distance)
        # # print("Approprieteness distance:", appropriateness_distance)
        np_info_dict[np]["caloric_Distance"] = caloric_distance
        np_info_dict[np]["protein_Distance"] = protein_distance
        np_info_dict[np]["fat_Distance"] = fat_distance
        np_info_dict[np]["Appropriateness_Distance"] = appropriateness_distance
    return np_info_dict


def nps_diversity(all_sorted_np_score_dicts):
    '''
    This function is responsible to check is the weekly meal plan is diverse enought.
    For example if the same meal is proposed more than 3 times we dont want it and
    more rules regarding the diversence. Now, dont ask me how this function exactly works.
    It was written by Kyriakos Kalpakoglou and I fear that even he can not tell us the
    exact funciton. If it works, dont touch it.
    '''
    d_not_unique_meals = [[], [], [], [], [], [], []]
    d_not_unique_nps = []
    final_meals = []
    final_meals_id = []
    final_dishes_id = []
    final_nps = []
    final_food_group_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    day = 0
    invalid_day = 0
    valid_days = [False, False, False, False, False, False, False]

    daily_rules_list = [0, 0, 0, 0, 0, 0, 0]

    for sorted_np_score_dict in all_sorted_np_score_dicts:
        for np in sorted_np_score_dict:
            if np in final_nps:
                continue

            cnt_fruit_salad = final_food_group_list[0] + sorted_np_score_dict[np]["Fruit_Salad"]
            cnt_processed_meat = final_food_group_list[1] + sorted_np_score_dict[np]["Processed_Meat"]
            cnt_red_meat = final_food_group_list[2] + sorted_np_score_dict[np]["Red_Meat"]
            cnt_white_meat = final_food_group_list[3] + sorted_np_score_dict[np]["White_Meat"]
            cnt_chicken = final_food_group_list[4] + sorted_np_score_dict[np]["Chicken"]
            cnt_turkey = final_food_group_list[5] + sorted_np_score_dict[np]["Turkey"]
            cnt_rabbit = final_food_group_list[6] + sorted_np_score_dict[np]["Rabbit"]
            cnt_pulses = final_food_group_list[7] + sorted_np_score_dict[np]["Pulses"]
            cnt_chickpeas = final_food_group_list[8] + sorted_np_score_dict[np]["Chickpeas"]
            cnt_lentils = final_food_group_list[9] + sorted_np_score_dict[np]["Lentils"]
            cnt_white_red_beans = final_food_group_list[10] + sorted_np_score_dict[np]["White_Red_Beans"]
            cnt_other_legumes = final_food_group_list[11] + sorted_np_score_dict[np]["Other_Legumes"]
            cnt_tubers = final_food_group_list[12] + sorted_np_score_dict[np]["Tubers"]
            cnt_rice = final_food_group_list[13] + sorted_np_score_dict[np]["Rice"]
            cnt_pasta = final_food_group_list[14] + sorted_np_score_dict[np]["Pasta"]
            cnt_fish = final_food_group_list[15] + sorted_np_score_dict[np]["Fish"]

            if (len(set(sorted_np_score_dict[np]["Dishes_id"])) == len(sorted_np_score_dict[np]["Dishes_id"])) and \
                (sorted_np_score_dict[np]["Eggs"] <= 1) and  \
                (cnt_processed_meat <= 0) and \
                (cnt_red_meat <= 3) and \
                (cnt_tubers <= 4) and \
                (cnt_rice <= 3) and \
                (cnt_pasta <= 3) and \
                (cnt_fish <= 2) and \
                sorted_np_score_dict[np]["Common_White_Meat"] is False and \
                sorted_np_score_dict[np]["Common_Red_Meat"] is False and \
                sorted_np_score_dict[np]["Common_Pork"] is False and \
                sorted_np_score_dict[np]["Common_Fish"] is False and \
                sorted_np_score_dict[np]["Common_Pulses"] is False and \
                sorted_np_score_dict[np]["Common_Pasta"] is False and \
                sorted_np_score_dict[np]["Common_Rice"] is False:

                meals_cnt = 0
                for j in range(5):
                    x = final_meals_id.count(sorted_np_score_dict[np]["Meals_id"][j])
                    if (sorted_np_score_dict[np]["Meals_id"][j] not in final_meals_id) or (x < 2):
                        meals_cnt += 1
                if meals_cnt == 5:
                    final_meals.append(sorted_np_score_dict[np]["Meals_id"])
                    final_nps.append(np)

                    final_food_group_list[0] += sorted_np_score_dict[np]["Fruit_Salad"]
                    final_food_group_list[1] += sorted_np_score_dict[np]["Processed_Meat"]
                    final_food_group_list[2] += sorted_np_score_dict[np]["Red_Meat"]
                    final_food_group_list[3] += sorted_np_score_dict[np]["White_Meat"]
                    final_food_group_list[4] += sorted_np_score_dict[np]["Chicken"]
                    final_food_group_list[5] += sorted_np_score_dict[np]["Turkey"]
                    final_food_group_list[6] += sorted_np_score_dict[np]["Rabbit"]
                    final_food_group_list[7] += sorted_np_score_dict[np]["Pulses"]
                    final_food_group_list[8] += sorted_np_score_dict[np]["Chickpeas"]
                    final_food_group_list[9] += sorted_np_score_dict[np]["Lentils"]
                    final_food_group_list[10] += sorted_np_score_dict[np]["White_Red_Beans"]
                    final_food_group_list[11] += sorted_np_score_dict[np]["Other_Legumes"]
                    final_food_group_list[12] += sorted_np_score_dict[np]["Tubers"]
                    final_food_group_list[13] += sorted_np_score_dict[np]["Rice"]
                    final_food_group_list[14] += sorted_np_score_dict[np]["Pasta"]
                    final_food_group_list[15] += sorted_np_score_dict[np]["Fish"]

                    final_meals_id.extend(sorted_np_score_dict[np]["Meals_id"][:5])
                    final_dishes_id.extend(sorted_np_score_dict[np]["Dishes_id"][:len(sorted_np_score_dict[np]["Dishes_id"])])

                    valid_days[day] = True
                    break
                else:
                    if len(d_not_unique_meals[day]) == 0:
                        d_not_unique_meals[day].append(sorted_np_score_dict[np]["Meals_id"])
                        d_not_unique_nps.append(np)
                    else:
                        pass
            else:
                if len(d_not_unique_meals[day]) == 0:
                    d_not_unique_meals[day].append(sorted_np_score_dict[np]["Meals_id"])
                    d_not_unique_nps.append(np)
                else:
                    pass
            if len(final_meals) == 7:
                break

        if len(final_meals) == 7:
            break
        day += 1

    i = 0
    for valid_day in valid_days:
        if valid_day:
            pass
        else:
            final_meals.insert(i, d_not_unique_meals[i][0])
            final_nps.append(d_not_unique_nps[i])
        i += 1
    return final_meals, valid_days, final_nps


def normalization(nutrient, target, length, case, limit1, limit2, divider, energy_intake):
    limits = [round(limit1*energy_intake/divider, 2), round(limit2*energy_intake/divider,2 )]
    avg = nutrient / length

    if case in ["carbs", "fats"]:
        normal = 1
        if  limits[0] <= avg <= limits[1]:
            normal = 0
            return f"avg: {avg:.2f}\ttarget: ({limits[0]:.2f},{limits[1]:.2f})\tstd: {normal:.2f}"
        else:
            if avg < limits[0]:
                normal = round(abs(avg - limits[0]) / limits[0], 2)
                return f"avg: {avg:.2f}\ttarget: ({limits[0]:.2f},{limits[1]:.2f})\tstd: {normal:.2f}"
            else:
                normal = round(abs(avg - limits[1]) / limits[1], 2)
                return f"avg: {avg:.2f}\ttarget: ({limits[0]:.2f},{limits[1]:.2f})\tstd: {normal:.2f}"
    else:
        distance = round(abs(target - avg), 2)
        normal = round(round(distance/target, 2), 2)
        return f"avg: {avg:.2f}\ttarget: {target:.2f}\t\tstd: {normal:.2f}"


def filter_cuisines(cuisines):
    print("Pilot country:", cuisines)
    try:
        return Meal.objects.filter(Country__in=cuisines)
    except:
        return None



