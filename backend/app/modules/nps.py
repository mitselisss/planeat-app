from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
from ..models import Dish, Meal, UserProfile, NP, NPItem
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
from datetime import date, timedelta
import datetime
import math


NUMBER_OF_SAMPLES = 100000
TOP_PLANS = 20
N_WEEKLY_COMBINATIOS = math.factorial(TOP_PLANS)/( math.factorial(TOP_PLANS-7) * math.factorial(7))
MEAL_COUNTER_THRESHOLD = 200000000
meal_counts = defaultdict(int)  # Track meal occurrences in heap
meat_count = 0 # Track meat occurrences in heap
oily_fish_count = 0 # Track oily fish occurrences in heap
fish_count = 0 # Track fish occurrences in heap


# NUTRITION_WEIGHTS = {
#     "energy": 10,
#     "protein": 2, "carb": 2, "fat": 2, "fibre": 2,
#     "calcium":1, "iron": 1, "folate": 1,
#     "veg_q": 6, "veg_s": 5,
#     "fru_q": 0, "fru_s": 2,
#     "jui_s": -1,
#     "plp_q": 1,
#     "dai_q": 1, "dai_s": 2,
#     "che_q": 1, "che_s": 0,
#     "nns_q": 1,
#     "mea_q": 4, "mea_s": 2,
#     "oif_q": 1, "oif_s": 1,
#     "fis_q": 1, "fis_s": 1,
# }

NUTRITION_WEIGHTS = {
    "energy": 10,
    "protein": 0, "carb": 0, "fat": 0, "fibre": 0,
    "calcium":0, "iron": 0, "folate": 0,
    "veg_q": 1, "veg_s": 1,
    "fru_q": 1, "fru_s": 1,
    "jui_s": 0,
    "plp_q": 0,
    "dai_q": 0, "dai_s": 0,
    "che_q": 0, "che_s": 0,
    "nns_q": 0,
    "mea_q": 0.1, "mea_s": 1,
    "oif_q": 1, "oif_s": 1,
    "fis_q": 1, "fis_s": 1,
    "meal_p": 0.1, "meat_p": 0.1, "oilf_p": 0.1, "fish_p": 0.1,
}

key_arguments = [
    "energy",
    "protein", "carb", "fat", "fibre",
    #"calcium", "iron", "folate",
    #"veg_q", "veg_s",
    #"fru_q", "fru_s",
    #"jui_s",
    #"plp_q",
    #"dai_q", "dai_s",
    #"che_q", "che_s",
    #"nns_q",
    #"mea_q", "mea_s",
    #"oif_q", "oif_s",
    #"fis_q", "fis_s",
]


def _filtering(cuisine, user_preference, user_allergy):
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
    }

    query = (
        SEASSON_FILTERS[season] &
        Q(Country__in=cuisine) &
        PREFERENCE_FILTERS.get(user_preference, Q()) &  # Default to empty Q if preference not found
        ALLERGY_FILTERS.get(user_allergy, Q())  # Default to empty Q if allergy not found
    )

    return Meal.objects.filter(query)


def _get_five_meals(meals):
    """Functions that returns the five meals"""
    meals = [
        meals.filter(Type="Breakfast"),
        meals.filter(Type="Snack"),
        meals.filter(Type="Lunch"),
        meals.filter(Type="Snack"),
        meals.filter(Type="Dinner")
    ]
    return meals


def _combinations(flag, results, sets, num_samples):
    if flag == "daily":
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
    elif flag == "weekly":
        """Generate meal combinations with smart sampling"""
        return combinations(results, 7)


def _calculate_nutrition(flag, meals):
    if flag == "weekly":
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
            "veg_s": sum(m['nutrition'].get('veg_s', 0) for m in meals),
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
            "oif_q": sum(m['nutrition'].get('oif_q', 0) for m in meals),
            "oif_s": sum(m['nutrition'].get('oif_s', 0) for m in meals),
            "fis_q": sum(m['nutrition'].get('fis_q', 0) for m in meals),
            "fis_s": sum(m['nutrition'].get('fis_s', 0) for m in meals),
        }

        return nutrition_totals

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
        if group in ["BA", "BAB", "BAE", "BAH", "BAK", "BAN", "BAR", "BC", "BL", "BN", "BNE", "BNH", "BNS"]:
            nutrition_totals["dai_s"] = totals["servings"]
            nutrition_totals["dai_q"] = totals["grams"]
        if group in ["BL"]:
            nutrition_totals["che_s"] = totals["servings"]
            nutrition_totals["che_q"] = totals["grams"]
        if group in ["G", "GA"]:
            nutrition_totals["nns_s"] = totals["servings"]
            nutrition_totals["nns_q"] = totals["grams"]
        if group in ["JC"]:
            nutrition_totals["oif_s"] = totals["servings"]
            nutrition_totals["oif_q"] = totals["grams"]
        if group in ["J", "JA", "JK", "JM", "JR"]:
            nutrition_totals["fis_s"] = totals["servings"]
            nutrition_totals["fis_q"] = totals["grams"]

    return nutrition_totals


def _in_range(predicted, target, serving):
    if serving:
        return abs(predicted-target)/target
    else:
        if abs(predicted-target)/target >= 1:
            return pow(abs(predicted-target)/target, 2)
        else:
            return abs(predicted-target)/target


def calculate_score(flag, nutrition, user_energy_intake, user_weight, user_sex):
    score = 0
    if flag == "weekly":
        score = _score_weekly(nutrition, user_energy_intake, user_weight, user_sex)
        return score
    elif flag == "daily":
        score += _score_energy(nutrition, user_energy_intake)
        score += _score_macronutrients(nutrition, user_energy_intake, user_weight)
        score += _score_micronutrients(nutrition, user_sex)
        score += _score_food_groups(nutrition)
        return score


def _score_energy(nutrition, energy_target):
    # Energy scoring
    score = NUTRITION_WEIGHTS["energy"] * _in_range(nutrition.get("energy", 0), energy_target, False)
    nutrition["energy_variable"] = _in_range(nutrition.get("energy", 0), energy_target, False)
    nutrition["energy_prediction"] = nutrition.get("energy", 0)
    nutrition["energy_target"] = energy_target
    return -score


def _score_macronutrients(nutrition, energy_target, user_weight):
    score = 0

    # Protein scoring
    protein_target = user_weight * 0.83
    score -= NUTRITION_WEIGHTS["protein"] * _in_range(nutrition.get("protein", 0), protein_target, False)
    nutrition["protein_variable"] = _in_range(nutrition.get("protein", 0), protein_target, False)
    nutrition["protein_prediction"] = nutrition.get("protein", 0)
    nutrition["protein_target"] = protein_target


    # Carb scoring
    # nutrition["carb_variable"] = 0
    # nutrition["carb_prediction"] = nutrition.get("carb", 0)
    # if 0.45*energy_target/4 <= nutrition.get("carb", 0) <= 0.6*energy_target/4:
    #     score += 10 * NUTRITION_WEIGHTS["carb"]
    #     nutrition["carb_variable"] = 10
    carb_target = 0.575*energy_target/4
    score -= NUTRITION_WEIGHTS["carb"] * _in_range(nutrition.get("carb", 0), carb_target, False)
    nutrition["carb_variable"] = _in_range(nutrition.get("carb", 0), carb_target, False)
    nutrition["carb_prediction"] = nutrition.get("carb", 0)
    nutrition["carb_target"] = carb_target

    # Fats scoring
    # nutrition["fat_variable"] = 0
    # nutrition["fat_prediction"] = nutrition.get("fat", 0)
    # if 0.2*energy_target/9 <= nutrition.get("fat", 0) <= 0.35*energy_target/9:
    #     score += 10 * NUTRITION_WEIGHTS["fat"]
    #     nutrition["fat_variable"] = 10
    fats_target = 0.325*energy_target/9
    score -= NUTRITION_WEIGHTS["fat"] * _in_range(nutrition.get("fat", 0), fats_target, False)
    nutrition["fat_variable"] = _in_range(nutrition.get("fat", 0), fats_target, False)
    nutrition["fat_prediction"] = nutrition.get("fat", 0)
    nutrition["fat_target"] = fats_target

    # Fibre scoring
    nutrition["fibre_variable"] = 0
    nutrition["fibre_prediction"] = nutrition.get("fibre", 0)
    # if nutrition.get("fibre", 0) > 22.5:
    #     score += 10 * NUTRITION_WEIGHTS["fibre"]
    #     nutrition["fibre_variable"] = 10
    # elif nutrition.get("fibre", 0) > 20:
    #     score += 5 * NUTRITION_WEIGHTS["fibre"]
    #     nutrition["fibre_variable"] = 5
    fibre_target = 22.5
    score -= NUTRITION_WEIGHTS["fibre"] * _in_range(nutrition.get("fibre", 0), fibre_target, False)
    nutrition["fibre_variable"] = _in_range(nutrition.get("fibre", 0), fibre_target, False)
    nutrition["fibre_prediction"] = nutrition.get("fibre", 0)
    nutrition["fibre_target"] = fibre_target

    return score


def _score_micronutrients(nutrition, user_sex):
    score = 0

    # Calcuim scoring
    calcium_target = 1000
    score -= NUTRITION_WEIGHTS["calcium"] * _in_range(nutrition.get("calcium", 0), calcium_target, False)
    nutrition["calcium_variable"] = _in_range(nutrition.get("calcium", 0), calcium_target, False)
    nutrition["calcium_prediction"] = nutrition.get("calcium", 0)
    nutrition["calcium_target"] = calcium_target

    # Iron scoring
    if user_sex in ["Male", "male"]:
        iron_target = 11
    elif user_sex in ["Female", "female"]:
        iron_target = 17
    score -= NUTRITION_WEIGHTS["iron"] * _in_range(nutrition.get("iron", 0), iron_target, False)
    nutrition["iron_variable"] = _in_range(nutrition.get("iron", 0), iron_target, False)
    nutrition["iron_prediction"] = nutrition.get("iron", 0)
    nutrition["iron_target"] = iron_target

    # Folate scoring
    folate_target = 330
    score -= NUTRITION_WEIGHTS["folate"] * _in_range(nutrition.get("folate", 0), folate_target, False)
    nutrition["folate_variable"] = _in_range(nutrition.get("folate", 0), folate_target, False)
    nutrition["folate_prediction"] = nutrition.get("folate", 0)
    nutrition["folate_target"] = folate_target

    return score


def _score_food_groups(nutrition):
    score = 0

    # Vegetable quantity scoring
    # if nutrition.get("veg_q", 0) > 270:
    #     score += 10 * NUTRITION_WEIGHTS["veg_q"]
    #     nutrition["veg_q_variable"] = 10
    # elif nutrition.get("veg_q", 0) > 240:
    #     score += 5 * NUTRITION_WEIGHTS["veg_q"]
    #     nutrition["veg_q_variable"] = 5
    veg_q_target = 300
    score -= NUTRITION_WEIGHTS["veg_q"] * _in_range(nutrition.get("veg_q", 0), veg_q_target, False)
    nutrition["veg_q_variable"] = _in_range(nutrition.get("veg_q", 0), veg_q_target, False)
    nutrition["veg_q_prediction"] = nutrition.get("veg_q", 0)
    nutrition["veg_q_target"] = veg_q_target

    # Vegetable serving scoring
    # if nutrition.get("veg_s", 0) > 2:
    #     score += 10 * NUTRITION_WEIGHTS["veg_s"]
    #     nutrition["veg_s_variable"] = 10
    # elif nutrition.get("veg_s", 0) > 1:
    #     score += 5 * NUTRITION_WEIGHTS["veg_s"]
    #     nutrition["veg_s_variable"] = 5
    veg_s_target = 3
    score -= NUTRITION_WEIGHTS["veg_s"] * _in_range(nutrition.get("veg_s", 0), veg_s_target, True)
    nutrition["veg_s_variable"] = _in_range(nutrition.get("veg_s", 0), veg_s_target, True)
    nutrition["veg_s_prediction"] = nutrition.get("veg_s", 0)
    nutrition["veg_s_target"] = veg_s_target

    # Fruit quantity scoring
    fruit_quantity_target = 200
    score -= NUTRITION_WEIGHTS["fru_q"] * _in_range(nutrition.get("fru_q", 0), fruit_quantity_target, False)
    nutrition["fru_q_variable"] = _in_range(nutrition.get("fru_q", 0), fruit_quantity_target, False)
    nutrition["fru_q_prediction"] = nutrition.get("fru_q", 0)
    nutrition["fru_q_target"] = fruit_quantity_target

    # Fruit serving scoring
    # if nutrition.get("fru_s", 0) == fruit_serving_target:
    #     score += 10 * NUTRITION_WEIGHTS["fru_s"]
    #     nutrition["fru_s_variable"] = 10
    # elif fruit_serving_target-1 <= nutrition.get("fru_s", 0) <= fruit_serving_target+1:
    #     score += 5 * NUTRITION_WEIGHTS["fru_s"]
    #     nutrition["fru_s_variable"] = 5
    fruit_serving_target = 2
    score -= NUTRITION_WEIGHTS["fru_s"] * _in_range(nutrition.get("fru_s", 0), fruit_serving_target, True)
    nutrition["fru_s_variable"] = _in_range(nutrition.get("fru_s", 0), fruit_serving_target, True)
    nutrition["fru_s_prediction"] = nutrition.get("fru_s", 0)
    nutrition["fru_s_target"] = fruit_serving_target

    # Juice serving scoring
    juice_serving_target = 1
    # if nutrition.get("Jui_s", 0) > juice_serving_target:
    #     score += -1 * NUTRITION_WEIGHTS["jui_s"]
    #     nutrition["jui_s_variable"] = -1
    score -= NUTRITION_WEIGHTS["jui_s"] * _in_range(nutrition.get("jui_s", 0), juice_serving_target, True)
    nutrition["jui_s_variable"] = _in_range(nutrition.get("jui_s", 0), juice_serving_target, True)
    nutrition["jui_s_prediction"] = nutrition.get("jui_s", 0)
    nutrition["jui_s_target"] = juice_serving_target

    # Plant protein quantity scoring
    # if nutrition.get("plp_q", 0) > 112.5:
    #     score += 10 * NUTRITION_WEIGHTS["plp_q"]
    #     nutrition["plp_q_variable"] = 10
    # elif nutrition.get("plp_q", 0) > 100:
    #     score += 5 * NUTRITION_WEIGHTS["plp_q"]
    #     nutrition["plp_q_variable"] = 5
    plp_q_target = 125
    score -= NUTRITION_WEIGHTS["plp_q"] * _in_range(nutrition.get("plp_q", 0), plp_q_target, False)
    nutrition["plp_q_variable"] = _in_range(nutrition.get("plp_q", 0), plp_q_target, False)
    nutrition["plp_q_prediction"] = nutrition.get("plp_q", 0)
    nutrition["plp_q_target"] = plp_q_target

    # Dairy quantity scoring
    # nutrition["dai_q_variable"] = 0
    # nutrition["dai_q_prediction"] = nutrition.get("dai_q", 0)
    # if 125 <= nutrition.get("dai_q", 0) <= 250:
    #     score += 10 * NUTRITION_WEIGHTS["dai_q"]
    #     nutrition["dai_q_variable"] = 10
    dai_q_target = 187.5
    score -= NUTRITION_WEIGHTS["dai_q"] * _in_range(nutrition.get("dai_q", 0), dai_q_target, False)
    nutrition["dai_q_variable"] = _in_range(nutrition.get("dai_q", 0), dai_q_target, False)
    nutrition["dai_q_prediction"] = nutrition.get("dai_q", 0)
    nutrition["dai_q_target"] = dai_q_target

    # Dairy serving scoring
    # nutrition["dai_s_variable"] = 0
    # nutrition["dai_s_prediction"] = nutrition.get("dai_s", 0)
    # if 1 <= nutrition.get("dai_s", 0) <= 2:
    #     score += 10 * NUTRITION_WEIGHTS["dai_s"]
    #     nutrition["dai_s_variable"] = 10
    dai_s_target = 2
    score -= NUTRITION_WEIGHTS["dai_s"] * _in_range(nutrition.get("dai_s", 0), dai_s_target, True)
    nutrition["dai_s_variable"] = _in_range(nutrition.get("dai_s", 0), dai_s_target, True)
    nutrition["dai_s_prediction"] = nutrition.get("dai_s", 0)
    nutrition["dai_s_target"] = dai_s_target

    # Cheese quantity scoring
    cheese_quantity_ratget = 25
    score -= NUTRITION_WEIGHTS["che_q"] * _in_range(nutrition.get("che_q", 0), cheese_quantity_ratget, False)
    nutrition["che_q_variable"] = _in_range(nutrition.get("che_q", 0), cheese_quantity_ratget, False)
    nutrition["che_q_prediction"] = nutrition.get("che_q", 0)
    nutrition["che_q_target"] = cheese_quantity_ratget

    # Cheese serving scoring
    # cheese_serving_ratget = 1
    # nutrition["che_s_variable"] = 0
    # nutrition["che_s_prediction"] = nutrition.get("che_s", 0)
    # if nutrition.get("che_s", 0) == 1:
    #     score += 10 * NUTRITION_WEIGHTS["che_s"]
    #     nutrition["che_s_variable"] = 10
    che_s_target = 1
    score -= NUTRITION_WEIGHTS["che_s"] * _in_range(nutrition.get("che_s", 0), che_s_target, True)
    nutrition["che_s_variable"] = _in_range(nutrition.get("che_s", 0), che_s_target, True)
    nutrition["che_s_prediction"] = nutrition.get("che_s", 0)
    nutrition["che_s_target"] = che_s_target

    # Nuts and seeds quantity scoring
    nuts_and_seeds_quantity_target = 30
    score -= NUTRITION_WEIGHTS["nns_q"] * _in_range(nutrition.get("nns_q", 0), nuts_and_seeds_quantity_target, False)
    nutrition["nns_q_variable"] = _in_range(nutrition.get("nns_q", 0), nuts_and_seeds_quantity_target, False)
    nutrition["nns_q_prediction"] = nutrition.get("nns_q", 0)
    nutrition["nns_q_target"] = nuts_and_seeds_quantity_target

    # Add meat to nutrition dictionary
    nutrition["mea_q_prediction"] = nutrition.get("mea_q", 0)
    nutrition["mea_q_variable"] = 0
    nutrition["mea_q_target"] = 0
    nutrition["mea_s_prediction"] = nutrition.get("mea_s", 0)
    nutrition["mea_s_variable"] = 0
    nutrition["mea_s_target"] = 0

    # Add oily fish to nutrition dictionary
    nutrition["oif_q_prediction"] = nutrition.get("oif_q", 0)
    nutrition["oif_q_variable"] = 0
    nutrition["oif_q_target"] = 0
    nutrition["oif_s_prediction"] = nutrition.get("oif_s", 0)
    nutrition["oif_s_variable"] = 0
    nutrition["oif_s_target"] = 0

    # Add fish to nutrition dictionary
    nutrition["fis_q_prediction"] = nutrition.get("fis_q", 0)
    nutrition["fis_q_variable"] = 0
    nutrition["fis_q_target"] = 0
    nutrition["fis_s_prediction"] = nutrition.get("fis_s", 0)
    nutrition["fis_s_variable"] = 0
    nutrition["fis_s_target"] = 0

    return score


def _score_weekly(nutrition, user_energy_target, user_weight, user_sex):
    """Modular scoring system with range checks"""
    score = 0.0

    # Energy scoring
    energy_target = user_energy_target * 7
    score -= NUTRITION_WEIGHTS["energy"] * _in_range(nutrition.get("energy", 0), energy_target, False)
    nutrition["energy_variable"] = _in_range(nutrition.get("energy", 0), energy_target, False)
    nutrition["energy_prediction"] = nutrition.get("energy", 0)
    nutrition["energy_target"] = energy_target

    # Protein scoring
    protein_target = user_weight * 0.83 * 7
    score -= NUTRITION_WEIGHTS["protein"] * _in_range(nutrition.get("protein", 0), protein_target, False)
    nutrition["protein_variable"] = _in_range(nutrition.get("protein", 0), protein_target, False)
    nutrition["protein_prediction"] = nutrition.get("protein", 0)
    nutrition["protein_target"] = protein_target

    # Carb scoring
    # nutrition["carb_variable"] = 0
    # nutrition["carb_prediction"] = nutrition.get("carb", 0)
    # if 0.45*energy_target/4 <= nutrition.get("carb", 0) <= 0.6*energy_target/4:
    #     score += 10 * NUTRITION_WEIGHTS["carb"]
    #     nutrition["carb_variable"] = 10
    carb_target = 0.575*user_energy_target/4  * 7
    score -= NUTRITION_WEIGHTS["carb"] * _in_range(nutrition.get("carb", 0), carb_target, False)
    nutrition["carb_variable"] = _in_range(nutrition.get("carb", 0), carb_target, False)
    nutrition["carb_prediction"] = nutrition.get("carb", 0)
    nutrition["carb_target"] = carb_target

    # Fats scoring
    # nutrition["fat_variable"] = 0
    # nutrition["fat_prediction"] = nutrition.get("fat", 0)
    # if 0.2*energy_target/9 <= nutrition.get("fat", 0) <= 0.35*energy_target/9:
    #     score += 10 * NUTRITION_WEIGHTS["fat"]
    #     nutrition["fat_variable"] = 10
    fat_target = 0.325*user_energy_target/9  * 7
    score -= NUTRITION_WEIGHTS["fat"] * _in_range(nutrition.get("fat", 0), fat_target, False)
    nutrition["fat_variable"] = _in_range(nutrition.get("fat", 0), fat_target, False)
    nutrition["fat_prediction"] = nutrition.get("fat", 0)
    nutrition["fat_target"] = fat_target

    # Fibre scoring
    # nutrition["fibre_variable"] = 0
    # nutrition["fibre_prediction"] = nutrition.get("fibre", 0)
    # if nutrition.get("fibre", 0) > 22.5  * 7:
    #     score += 10 * NUTRITION_WEIGHTS["fibre"]
    #     nutrition["fibre_variable"] = 10
    # elif nutrition.get("fibre", 0) > 20:
    #     score += 5 * NUTRITION_WEIGHTS["fibre"]
    #     nutrition["fibre_variable"] = 5
    # nutrition["fibre_target"] = 22.5  * 7
    fibre_target = 22.5  * 7
    score -= NUTRITION_WEIGHTS["fibre"] * _in_range(nutrition.get("fibre", 0), fibre_target, False)
    nutrition["fibre_variable"] = _in_range(nutrition.get("fibre", 0), fibre_target, False)
    nutrition["fibre_prediction"] = nutrition.get("fibre", 0)
    nutrition["fibre_target"] = fibre_target

    # Calcuim scoring
    calcium_target = 1000 * 7
    score -= NUTRITION_WEIGHTS["calcium"] * _in_range(nutrition.get("calcium", 0), calcium_target, False)
    nutrition["calcium_variable"] = _in_range(nutrition.get("calcium", 0), calcium_target, False)
    nutrition["calcium_prediction"] = nutrition.get("calcium", 0)
    nutrition["calcium_target"] = calcium_target

    # Iron scoring
    if user_sex in ["Male", "male"]:
        iron_target = 11  * 7
    elif user_sex in ["Female", "female"]:
        iron_target = 17  * 7
    score -= NUTRITION_WEIGHTS["iron"] * _in_range(nutrition.get("iron", 0), iron_target, False)
    nutrition["iron_variable"] = _in_range(nutrition.get("iron", 0), iron_target, False)
    nutrition["iron_prediction"] = nutrition.get("iron", 0)
    nutrition["iron_target"] = iron_target

    # Folate scoring
    folate_target = 330  * 7
    score -= NUTRITION_WEIGHTS["folate"] * _in_range(nutrition.get("folate", 0), folate_target, False)
    nutrition["folate_variable"] = _in_range(nutrition.get("folate", 0), folate_target, False)
    nutrition["folate_prediction"] = nutrition.get("folate", 0)
    nutrition["folate_target"] = folate_target

    # Vegetable quantity scoring
    veg_q_target = 300 * 7
    #score -= NUTRITION_WEIGHTS["veg_q"] * _in_range(nutrition.get("veg_q", 0), veg_q_target, False)
    nutrition["veg_q_variable"] = _in_range(nutrition.get("veg_q", 0), veg_q_target, False)
    nutrition["veg_q_prediction"] = nutrition.get("veg_q", 0)
    nutrition["veg_q_target"] = veg_q_target

    # Vegetable serving scoring
    veg_s_target = 3 * 7
    #score -= NUTRITION_WEIGHTS["veg_s"] * _in_range(nutrition.get("veg_s", 0), veg_s_target, True)
    nutrition["veg_s_variable"] = _in_range(nutrition.get("veg_s", 0), veg_s_target, True)
    nutrition["veg_s_prediction"] = nutrition.get("veg_s", 0)
    nutrition["veg_s_target"] = veg_s_target

    # Fruit quantity scoring
    fruit_quantity_target = 200 * 7
    #score -= NUTRITION_WEIGHTS["fru_q"] * _in_range(nutrition.get("fru_q", 0), fruit_quantity_target, False)
    nutrition["fru_q_variable"] = _in_range(nutrition.get("fru_q", 0), fruit_quantity_target, False)
    nutrition["fru_q_prediction"] = nutrition.get("fru_q", 0)
    nutrition["fru_q_target"] = fruit_quantity_target

    # Fruit serving scoring
    fruit_serving_target = 2 * 7
    #score -= NUTRITION_WEIGHTS["fru_s"] * _in_range(nutrition.get("fru_s", 0), fruit_serving_target, True)
    nutrition["fru_s_variable"] = _in_range(nutrition.get("fru_s", 0), fruit_serving_target, True)
    nutrition["fru_s_prediction"] = nutrition.get("fru_s", 0)
    nutrition["fru_s_target"] = fruit_serving_target

    # Juice serving scoring
    juice_serving_target = 1 * 7
    #score -= NUTRITION_WEIGHTS["jui_s"] * _in_range(nutrition.get("jui_s", 0), juice_serving_target, True)
    nutrition["jui_s_variable"] = _in_range(nutrition.get("jui_s", 0), juice_serving_target, True)
    nutrition["jui_s_prediction"] = nutrition.get("jui_s", 0)
    nutrition["jui_s_target"] = juice_serving_target

    # Plant protein quantity scoring
    plp_q_target = 125 * 7
    #score -= NUTRITION_WEIGHTS["plp_q"] * _in_range(nutrition.get("plp_q", 0), plp_q_target, False)
    nutrition["plp_q_variable"] = _in_range(nutrition.get("plp_q", 0), plp_q_target, False)
    nutrition["plp_q_prediction"] = nutrition.get("plp_q", 0)
    nutrition["plp_q_target"] = plp_q_target

    # Dairy quantity scoring
    dai_q_target = 187.5 * 7
    #score -= NUTRITION_WEIGHTS["dai_q"] * _in_range(nutrition.get("dai_q", 0), dai_q_target, False)
    nutrition["dai_q_variable"] = _in_range(nutrition.get("dai_q", 0), dai_q_target, False)
    nutrition["dai_q_prediction"] = nutrition.get("dai_q", 0)
    nutrition["dai_q_target"] = dai_q_target

    # Dairy serving scoring
    dai_s_target = 2 * 7
    #score -= NUTRITION_WEIGHTS["dai_s"] * _in_range(nutrition.get("dai_s", 0), dai_s_target, True)
    nutrition["dai_s_variable"] = _in_range(nutrition.get("dai_s", 0), dai_s_target, True)
    nutrition["dai_s_prediction"] = nutrition.get("dai_s", 0)
    nutrition["dai_s_target"] = dai_s_target

    # Cheese quantity scoring
    cheese_quantity_ratget = 25 * 7
    #score -= NUTRITION_WEIGHTS["che_q"] * _in_range(nutrition.get("che_q", 0), cheese_quantity_ratget, False)
    nutrition["che_q_variable"] = _in_range(nutrition.get("che_q", 0), cheese_quantity_ratget, False)
    nutrition["che_q_prediction"] = nutrition.get("che_q", 0)
    nutrition["che_q_target"] = cheese_quantity_ratget

    # Cheese serving scoring
    che_s_target = 1 * 7
    #score -= NUTRITION_WEIGHTS["che_s"] * _in_range(nutrition.get("che_s", 0), che_s_target, True)
    nutrition["che_s_variable"] = _in_range(nutrition.get("che_s", 0), che_s_target, True)
    nutrition["che_s_prediction"] = nutrition.get("che_s", 0)
    nutrition["che_s_target"] = che_s_target

    # Nuts and seeds quantity scoring
    nuts_and_seeds_quantity_target = 30 * 7
    #score -= NUTRITION_WEIGHTS["nns_q"] * _in_range(nutrition.get("nns_q", 0), nuts_and_seeds_quantity_target, False)
    nutrition["nns_q_variable"] = _in_range(nutrition.get("nns_q", 0), nuts_and_seeds_quantity_target, False)
    nutrition["nns_q_prediction"] = nutrition.get("nns_q", 0)
    nutrition["nns_q_target"] = nuts_and_seeds_quantity_target

    # Meat quantity scoring
    meat_quantity_target = 420
    score -= NUTRITION_WEIGHTS["mea_q"] * _in_range(nutrition.get("mea_q", 0), meat_quantity_target, False)
    nutrition["mea_q_variable"] = _in_range(nutrition.get("mea_q", 0), meat_quantity_target, False)
    nutrition["mea_q_prediction"] = nutrition.get("mea_q", 0)
    nutrition["mea_q_target"] = meat_quantity_target

    # Meat serving scoring
    meat_serving_target = 3
    score -= NUTRITION_WEIGHTS["mea_s"] * _in_range(nutrition.get("mea_s", 0), meat_serving_target, True)
    nutrition["mea_s_variable"] = _in_range(nutrition.get("mea_s", 0), meat_serving_target, True)
    nutrition["mea_s_prediction"] = nutrition.get("mea_s", 0)
    nutrition["mea_s_target"] = meat_serving_target

    # Oily fish quantity scoring
    oif_quantity_target = 100
    score -= NUTRITION_WEIGHTS["oif_q"] * _in_range(nutrition.get("oif_q", 0), oif_quantity_target, False)
    nutrition["oif_q_variable"] = _in_range(nutrition.get("oif_q", 0), oif_quantity_target, False)
    nutrition["oif_q_prediction"] = nutrition.get("oif_q", 0)
    nutrition["oif_q_target"] = oif_quantity_target

    # Oily fish serving scoring
    oif_serving_target = 1
    score -= NUTRITION_WEIGHTS["oif_s"] * _in_range(nutrition.get("oif_s", 0), oif_serving_target, True)
    nutrition["oif_s_variable"] = _in_range(nutrition.get("oif_s", 0), oif_serving_target, True)
    nutrition["oif_s_prediction"] = nutrition.get("oif_s", 0)
    nutrition["oif_s_target"] = oif_serving_target

    # Fish quantity scoring
    fis_quantity_target = 200
    score -= NUTRITION_WEIGHTS["fis_q"] * _in_range(nutrition.get("fis_q", 0), fis_quantity_target, False)
    nutrition["fis_q_variable"] = _in_range(nutrition.get("fis_q", 0), fis_quantity_target, False)
    nutrition["fis_q_prediction"] = nutrition.get("fis_q", 0)
    nutrition["fis_q_target"] = fis_quantity_target

    # Fish serving scoring
    fis_serving_target = 2
    score -= NUTRITION_WEIGHTS["fis_s"] * _in_range(nutrition.get("fis_s", 0), fis_serving_target, True)
    nutrition["fis_s_variable"] = _in_range(nutrition.get("fis_s", 0), fis_serving_target, True)
    nutrition["fis_s_prediction"] = nutrition.get("fis_s", 0)
    nutrition["fis_s_target"] = fis_serving_target

    return score


def _update_meal_counts(meal_ids: List[int], increment: bool):
    """Properly handle meal count updates"""
    delta = 1 if increment else -1
    for i, m in enumerate(meal_ids):
        #if i in [0, 2, 4]:  # Only track main meals
        meal_counts[m] += delta


def _update_meat_counts(mea_s, increment: bool):
    """Properly handle meat count updates"""
    global meat_count
    delta = 1 if increment else -1
    meat_count += delta*mea_s


def _update_oily_fish_counts(oif_s, increment: bool):
    """Properly handle oily fish count updates"""
    global oily_fish_count
    delta = 1 if increment else -1
    oily_fish_count += delta*oif_s


def _update_fish_counts(fis_s, increment: bool):
    """Properly handle meat count updates"""
    global fish_count
    delta = 1 if increment else -1
    fish_count += delta*fis_s


def _process(flag, meals, user_energy_intake, user_weight, user_sex, results):
    """Main processing pipeline"""

    top_plans = []
    if flag == "daily":
        temp_list = []
        total_combinations = len(meals[0])*len(meals[1])*len(meals[2])*len(meals[3])*len(meals[4])
        print("Total combinations:", total_combinations)
        if total_combinations > NUMBER_OF_SAMPLES:
            combinations = _combinations("daily", results, meals, NUMBER_OF_SAMPLES)
        else:
            combinations = _combinations("daily", results, meals, total_combinations)
        print("Final combinations:", len(combinations))

        for idx, combo in enumerate(combinations):
            meal_ids = tuple(m.id for m in combo)
            nutrition = _calculate_nutrition("daily", combo)
            score = calculate_score("daily", nutrition, user_energy_intake, user_weight, user_sex)
            temp_list.append(meal_ids)

            # Adjust score based on meal diversity
            meal_diversity_penalty = sum(meal_counts[m.id] for m in combo) * NUTRITION_WEIGHTS["meal_p"]  # Small penalty for repetition
            score -= meal_diversity_penalty  # Reduce score if meals repeat

            # Adjust score based on meat amount
            meat_amount_penalty = meat_count * NUTRITION_WEIGHTS["meat_p"]  # Small penalty for meat
            score -= meat_amount_penalty  # Reduce score if meat repeat

            # Adjust score based on oily fish amount
            oily_fish_amount_penalty = oily_fish_count * NUTRITION_WEIGHTS["oilf_p"]  # Small penalty for oily fish
            score -= oily_fish_amount_penalty  # Reduce score if oily fish repeat

            # Adjust score based on fish amount
            fish_amount_penalty = fish_count * NUTRITION_WEIGHTS["fish_p"]  # Small penalty for fish
            score -= fish_amount_penalty  # Reduce score if fish repeat

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
                "np_idx": idx
            })

            #if all(meal_counts[m] < MEAL_COUNTER_THRESHOLD for m in meal_ids):
            if len(top_plans) <= TOP_PLANS:
                heapq.heappush(top_plans, entry)
                _update_meal_counts(meal_ids, increment=True)
                _update_meat_counts(nutrition.get("mea_s", 0), increment=True)
                _update_oily_fish_counts(nutrition.get("oif_s", 0), increment=True)
                _update_fish_counts(nutrition.get("fis_s", 0), increment=True)
            else:
                if score > top_plans[0][0]:
                    removed = heapq.heappop(top_plans)
                    _update_meal_counts(removed[2]["meals"], increment=False)
                    _update_meat_counts(removed[2]["nutrition"].get("mea_s", 0), increment=False)
                    _update_oily_fish_counts(removed[2]["nutrition"].get("oif_s", 0), increment=False)
                    _update_fish_counts(removed[2]["nutrition"].get("fis_s", 0), increment=False)
                    heapq.heappush(top_plans, entry)
                    _update_meal_counts(meal_ids, increment=True)
                    _update_meat_counts(nutrition.get("mea_s", 0), increment=True)
                    _update_oily_fish_counts(nutrition.get("oif_s", 0), increment=True)
                    _update_fish_counts(nutrition.get("fis_s", 0), increment=True)
    elif flag == "weekly":
        combinations = _combinations("weekly", results, 0, 0)

        for idx, combo in enumerate(combinations):
            if idx == N_WEEKLY_COMBINATIOS:
                break

            nutrition = _calculate_nutrition("weekly", combo)
            score = calculate_score("weekly", nutrition, user_energy_intake, user_weight, user_sex)

            entry = (score, idx, {
                "meals": [m['meals'] for m in combo],
                "score": score,
                "nutrition": nutrition,
                "np_idx": [c["np_idx"] for c in combo]
            })

            heapq.heappush(top_plans, entry)

            if len(top_plans) > TOP_PLANS:
                heapq.heappop(top_plans)

    print("meat      --->", meat_count)
    print("oily fish --->", oily_fish_count)
    print("fish      --->", fish_count)
    return sorted([plan[2] for plan in top_plans], key=lambda x: -x["score"])


@api_view(['GET'])
def create_nps(request, user_id, week_monday, week_sunday):
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

    print("Energy_Intake", user_profile.Energy_Intake)
    print("Weight", user_profile.Weight)
    meals = _filtering(user_profile.Selected_Cuisines, user_profile.Preferences, user_profile.Allergies)
    print("Number of meals after filtering:", len(meals))
    meals = _get_five_meals(meals)
    print("Breakfasts:", len(meals[0]))
    print("Morning Snacks:", len(meals[1]))
    print("Lunches:", len(meals[2]))
    print("Afternoon Snack:", len(meals[3]))
    print("Dinners:", len(meals[4]))

    daily_results = _process("daily", meals, user_profile.Energy_Intake, user_profile.Weight, user_profile.Sex, 0)
    daily_dataframe_transform(daily_results)

    weekly_results = _process("weekly", meals, user_profile.Energy_Intake, user_profile.Weight, user_profile.Sex, daily_results)
    weekly_dataframe_transform(weekly_results)

    print_best_week(weekly_results[0])

    # Code to retrieve the number of weeks a user has NP for for the new weekly NP to be created.
    # For example, if a user has 2 weekly NPs the new weekly generated NP must be saved for week 3.
    try:
        # Get the weekly NPs for the current user.
        user_np = NP.objects.filter(UserProfile=user_profile)
        if len(user_np) == 0:
            week = 1
        else:
            # Get the number of the last week and increase it by one so the
            # new created weekly NP will be for the new week.
            week = user_np[len(user_np)-1].week + 1
    except ImportError:
        return JsonResponse({'error': f'Could not get the nps for user:{user_id}.'}, status=400)
    _save_np(user_profile, week_monday, week_sunday, week, weekly_results[0])

    return JsonResponse({'message': f"NP created."}, status=200)


def _save_np(user_profile, week_monday, week_sunday, week, weekly_results):
    # Create an NP for this user for this week.
    np = NP.objects.create(
        UserProfile=user_profile,
        user_energy_intake=user_profile.Energy_Intake,
        start_date=week_monday,
        end_date=week_sunday,
        week=week
    )

    # Keep the days of the week into a list.
    days = ["Monday", "Tuesday", "Wednesday",
           "Thursday", "Friday", "Saturday", "Sunday"]
    # Keep the meal types into a list.
    meal_types = ["Breakfast", "Morning Snack",
                 "Lunch", "Afternoon Snack", "Dinner"]

    # Iterate through the final weekly meals.
    for i, day in enumerate(days):
        for j, meal_type in enumerate(meal_types):
            npitem = NPItem.objects.create(
                np=np,
                meal=Meal.objects.get(id=weekly_results["meals"][i][j]),
                day=day,
                meal_type=meal_type,
            )
            print(np, Meal.objects.get(id=weekly_results["meals"][i][j]), day, meal_type)


def print_best_week(result: List[Dict]):
    # Define day labels
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Define meal labels (optional)
    meal_labels = ["Breakfast", "Snack_1", "Lunch", "Snack_2", "Dinner"]

    # Create DataFrame
    df = pd.DataFrame(result['meals'], index=days_of_week, columns=meal_labels).T

    # Display DataFrame
    print(df)

    print("#######################")
    print(result["np_idx"])
    print()
    #print(result)

    # Mapping the keys in `nutrition` to the row names
    key_mapping = {
        'energy': "energy in kcal",
        'protein': "protein in gr", 'carb': "carb in gr", 'fat': "fat in gr", 'fibre': "fibre in gr",
        'calcium': "calcium in mgr", 'iron': "iron in mgr", 'folate': "folate in mcg",
        'veg_q': "veg_q in gr", 'veg_s': "veg_s servings",
        'fru_q': "fru_q in gr", 'fru_s': "fru_s servings",
        'jui_s': "jui_s servings",
        'plp_q': "plp_q in gr",
        'dai_q': "dai_q in gr", 'dai_s': "dai_s servings",
        'che_q': "che_q in gr", 'che_s': "che_s servings",
        'nns_q': "nns_q in gr",
        'mea_q': "mea_q in gr", 'mea_s': "mea_s servings",
        'oif_q': "oif_q in gr", 'oif_s': "oif_s servings",
        'fis_q': "fis_q in gr", 'fis_s': "fis_s servings",
    }

    # Preparing data for the DataFrame
    data = []
    for key, row_name in key_mapping.items():
        target = result["nutrition"].get(f"{key}_target", 0)
        predicted = result["nutrition"].get(f"{key}_prediction", 0)
        offset = result["nutrition"].get(f"{key}_variable", 0)
        data.append([row_name, target, predicted, offset])

    # Create the DataFrame
    df = pd.DataFrame(data, columns=["Nutrient", "Target", "Predicted", "Offset"])

    # Display the DataFrame
    print(df)


def weekly_dataframe_transform(results: List[Dict]):
    """Transform the results into a dataframe"""
    print()
    meal_plans_list = []
    meal_plans_list = []
    for plan in results:
        meal_plan = {"Score": f"{plan['score']:.3f}",}
        for key in key_arguments:
            meal_plan[f"{key}_t"] = f"{plan['nutrition'][f'{key}_target']:.1f}"
            meal_plan[f"{key}_p"] = f"{int(plan['nutrition'][f'{key}_prediction'])}"
            meal_plan[f"{key}_d"] = f"{plan['nutrition'][f'{key}_variable']:.4f}"
        meal_plans_list.append(meal_plan)
    df = pd.DataFrame(meal_plans_list)
    df = df.apply(pd.to_numeric, errors='ignore')
    averages = df.mean(numeric_only=True)
    df = pd.concat([df, pd.DataFrame(averages.to_dict(), index=["Avg"])])
    pd.options.display.float_format = '{:.3f}'.format
    print(df)


def daily_dataframe_transform(results: List[Dict]):
    """Transform the results into a dataframe"""
    print()
    meal_plans_list = []
    for plan in results:
        meal_plan = {"Score": f"{plan['score']:.3f}",}
        for key in key_arguments:
            meal_plan[f"{key}_t"] = f"{plan['nutrition'][f'{key}_target']:.1f}"
            meal_plan[f"{key}_p"] = f"{int(plan['nutrition'][f'{key}_prediction'])}"
            meal_plan[f"{key}_d"] = f"{plan['nutrition'][f'{key}_variable']:.1f}"
        meal_plans_list.append(meal_plan)
    df = pd.DataFrame(meal_plans_list)
    df = df.apply(pd.to_numeric, errors='ignore')
    averages = df.mean(numeric_only=True)
    df = pd.concat([df, pd.DataFrame(averages.to_dict(), index=["Avg"])])
    pd.options.display.float_format = '{:.3f}'.format
    print(df)

