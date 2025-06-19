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
from datetime import date, timedelta
from django.db.models import Q
import random

N_MEAL_PLANS = 200000
TOP_PLANS = 20

class DailyMealPlanGenerator:
    NUTRITION_WEIGHTS = {
        "energy": 10,
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
        "jui_s": 1.0,
        "leg_q": 0.06,
        "dai_q": 0.02,
        "dai_s": 0.01,
        "che_q": 0.02,
        "che_s": 0.01,
        "nns_q": 0.06,
        "fis_q": 0.1,
        "fis_s": 0.1,
        "oif_q": 0.1,
        "oif_s": 0.1,
    }

    def __init__(self):
        self.sex = "Male"
        self.user_weight = 80
        self.base_energy_intake = 2500
        self.user_energy_intake = 3324
        self.user_preference = "omnivore"
        self.user_allergy = "none"
        self.cuisine = [
                        "Irish",
                        "Spain",
                        "Hungary",
                        ]
        
        self.NUMBER_OF_SAMPLES = 100000
        self.TOP_PLANS = 20
        
        self.meal_counts = defaultdict(int)
        
        self.energy_target = self.user_energy_intake
        self.protein_target = [self.user_energy_intake * 0.15/4, self.user_energy_intake * 0.25/4]
        self.carbs_target = [self.user_energy_intake * 0.45/4, self.user_energy_intake * 0.6/4]
        self.fats_target = [self.user_energy_intake * 0.2/9, self.user_energy_intake * 0.35/9]
        self.fibre_target = 25
        self.calcium_target = 1000
        self.iron_target = 11 if self.sex == "Female" else 17
        self.folate_target = 330
        self.veg_q_target = self.user_energy_intake*300/self.base_energy_intake
        self.veg_s_target = 3
        self.fru_q_target = self.user_energy_intake*200/self.base_energy_intake
        self.fru_s_target = 2
        self.jui_s_target = 1
        self.leg_q_target = self.user_energy_intake*125/self.base_energy_intake
        self.dai_q_target = [self.user_energy_intake*125/self.base_energy_intake, self.user_energy_intake*250/self.base_energy_intake]
        self.dai_s_target = [1, 2]
        self.che_q_target = self.user_energy_intake*25/self.base_energy_intake
        self.che_s_target = 1
        self.nns_q_target = self.user_energy_intake*30/self.base_energy_intake
        self.mea_q_target = 420
        self.mea_s_target = 3
        self.fis_q_target = 200
        self.fis_s_target = 2
        self.oif_q_target = 100
        self.oif_s_target = 1

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
        }

        query = (
            SEASSON_FILTERS[season] &
            Q(Country__in=self.cuisine) &
            PREFERENCE_FILTERS.get(self.user_preference, Q()) &  # Default to empty Q if preference not found
            ALLERGY_FILTERS.get(self.user_allergy, Q())  # Default to empty Q if allergy not found
        )

        return Meal.objects.filter(query)

    def _get_five_meals(self, meals):
        """Functions that returns the five meals"""
        meals = [
            meals.filter(Type="Breakfast"),
            meals.filter(Type="Snack"),
            meals.filter(Type="Lunch"),
            meals.filter(Type="Snack"),
            meals.filter(Type="Dinner")
        ]
        return meals

    def _combinations(self, results, sets, num_samples):
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

    def calculate_nutrition(self, meals):
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
                nutrition_totals["leg_s"] = totals["servings"]
                nutrition_totals["leg_q"] = totals["grams"]
            if group in ["BA", "BC", "BL", "BN"]:
                nutrition_totals["dai_s"] = totals["servings"]
                nutrition_totals["dai_q"] = totals["grams"]
            if group in ["BL"]:
                nutrition_totals["che_s"] = totals["servings"]
                nutrition_totals["che_q"] = totals["grams"]
            if group in ["G", "GA"]:
                nutrition_totals["nns_s"] = totals["servings"]
                nutrition_totals["nns_q"] = totals["grams"]
            if group in ["J", "JA", "JK", "JM", "JR"]:
                nutrition_totals["fis_s"] = totals["servings"]
                nutrition_totals["fis_q"] = totals["grams"]
            if group in ["JC"]:
                nutrition_totals["oif_s"] = totals["servings"]
                nutrition_totals["oif_q"] = totals["grams"]

        return nutrition_totals

    def _distance(self, prediction, target):
        return abs(prediction - target)/target

    def score_daily_meal_plan(self, nutrition):
        """Modular scoring system with range checks"""
        
        score = 0.0
        
        # Energy scoring
        nutrition["energy_prediction"] = nutrition.get("energy", 0)
        score -= self.NUTRITION_WEIGHTS["energy"] * self._distance(nutrition["energy_prediction"], self.energy_target)
        nutrition["energy_variable"] = self._distance(nutrition["energy_prediction"], self.energy_target)

        # Protein scoring
        nutrition["protein_prediction"] = nutrition.get("protein", 0)
        if nutrition["protein_prediction"] >= self.protein_target[0] and nutrition["protein_prediction"] <= self.protein_target[1]:
            score -= 0
            nutrition["protein_variable"] = 0
        elif nutrition["protein_prediction"] < self.protein_target[0]:
            score -= self.NUTRITION_WEIGHTS["protein"] * self._distance(nutrition["protein_prediction"], self.protein_target[0])
            nutrition["protein_variable"] = self._distance(nutrition["protein_prediction"], self.protein_target[0])
        elif nutrition["protein_prediction"] > self.protein_target[1]:
            score -= self.NUTRITION_WEIGHTS["protein"] * self._distance(nutrition["protein_prediction"], self.protein_target[1])
            nutrition["protein_variable"] = self._distance(nutrition["protein_prediction"], self.protein_target[1])

        # Carb scoring
        nutrition["carb_prediction"] = nutrition.get("carb", 0)
        if nutrition["carb_prediction"] >= self.carbs_target[0] and nutrition["carb_prediction"] <= self.carbs_target[1]:
            score -= 0
            nutrition["carb_variable"] = 0
        elif nutrition["carb_prediction"] < self.carbs_target[0]:
            score -= self.NUTRITION_WEIGHTS["carb"] * self._distance(nutrition["carb_prediction"], self.carbs_target[0])
            nutrition["carb_variable"] = self._distance(nutrition["carb_prediction"], self.carbs_target[0])
        elif nutrition["carb_prediction"] > self.carbs_target[1]:
            score -= self.NUTRITION_WEIGHTS["carb"] * self._distance(nutrition["carb_prediction"], self.carbs_target[1])
            nutrition["carb_variable"] = self._distance(nutrition["carb_prediction"], self.carbs_target[1])

        # Fats scoring
        nutrition["fat_prediction"] = nutrition.get("fat", 0)
        if nutrition["fat_prediction"] >= self.fats_target[0] and nutrition["fat_prediction"] <= self.fats_target[1]:
            score -= 0
            nutrition["fat_variable"] = 0
        elif nutrition["fat_prediction"] < self.fats_target[0]:
            score -= self.NUTRITION_WEIGHTS["fat"] * self._distance(nutrition["fat_prediction"], self.fats_target[0])
            nutrition["fat_variable"] = self._distance(nutrition["fat_prediction"], self.fats_target[0])
        elif nutrition["fat_prediction"] > self.fats_target[1]:
            score -= self.NUTRITION_WEIGHTS["fat"] * self._distance(nutrition["fat_prediction"], self.fats_target[1])
            nutrition["fat_variable"] = self._distance(nutrition["fat_prediction"], self.fats_target[1])

        # Fibre scoring
        nutrition["fibre_prediction"] = nutrition.get("fibre", 0)
        score -= self.NUTRITION_WEIGHTS["fibre"] * self._distance(nutrition["fibre_prediction"], self.fibre_target)
        nutrition["fibre_variable"] = self._distance(nutrition["fibre_prediction"], self.fibre_target)

        # Calcuim scoring
        nutrition["calcium_prediction"] = nutrition.get("calcium", 0)
        score -= self.NUTRITION_WEIGHTS["calcium"] * self._distance(nutrition["calcium_prediction"], self.calcium_target)
        nutrition["calcium_variable"] = self._distance(nutrition["calcium_prediction"], self.calcium_target)

        # Iron scoring
        nutrition["iron_prediction"] = nutrition.get("iron", 0)
        score -= self.NUTRITION_WEIGHTS["iron"] * self._distance(nutrition["iron_prediction"], self.iron_target)
        nutrition["iron_variable"] = self._distance(nutrition["iron_prediction"], self.iron_target)

        # Folate scoring
        nutrition["folate_prediction"] = nutrition.get("folate", 0)
        score -= self.NUTRITION_WEIGHTS["folate"] * self._distance(nutrition["folate_prediction"], self.folate_target)
        nutrition["folate_variable"] = self._distance(nutrition["folate_prediction"], self.folate_target)

        # Vegetable quantity scoring
        nutrition["veg_q_prediction"] = nutrition.get("veg_q", 0)
        score -= self.NUTRITION_WEIGHTS["veg_q"] * self._distance(nutrition["veg_q_prediction"], self.veg_q_target)
        nutrition["veg_q_variable"] = self._distance(nutrition["veg_q_prediction"], self.veg_q_target)

        # Vegetable serving scoring
        nutrition["veg_s_prediction"] = nutrition.get("veg_s", 0)
        score -= self.NUTRITION_WEIGHTS["veg_s"] * self._distance(nutrition["veg_s_prediction"], self.veg_s_target)
        nutrition["veg_s_variable"] = self._distance(nutrition["veg_s_prediction"], self.veg_s_target)

        # Fruit quantity scoring
        nutrition["fru_q_prediction"] = nutrition.get("fru_q", 0)
        score -= self.NUTRITION_WEIGHTS["fru_q"] * self._distance(nutrition["fru_q_prediction"], self.fru_q_target)
        nutrition["fru_q_variable"] = self._distance(nutrition["fru_q_prediction"], self.fru_q_target)
        
        # Fruit serving scoring
        nutrition["fru_s_prediction"] = nutrition.get("fru_s", 0)
        score -= self.NUTRITION_WEIGHTS["fru_s"] * self._distance(nutrition["fru_s_prediction"], self.fru_s_target)
        nutrition["fru_s_variable"] = self._distance(nutrition["fru_s_prediction"], self.fru_s_target)

        # Juice serving scoring
        nutrition["jui_s_prediction"] = nutrition.get("jui_s", 0)
        score -= self.NUTRITION_WEIGHTS["jui_s"] * self._distance(nutrition["jui_s_prediction"], self.jui_s_target)
        nutrition["jui_s_variable"] = self._distance(nutrition["jui_s_prediction"], self.jui_s_target)


        # Plant protein quantity scoring
        nutrition["leg_q_prediction"] = nutrition.get("leg_q", 0)
        score -= self.NUTRITION_WEIGHTS["leg_q"] * self._distance(nutrition["leg_q_prediction"], self.leg_q_target)
        nutrition["leg_q_variable"] = self._distance(nutrition["leg_q_prediction"], self.leg_q_target)

        # Dairy quantity scoring
        nutrition["dai_q_variable"] = 0
        nutrition["dai_q_prediction"] = nutrition.get("dai_q", 0)
        if nutrition["dai_q_prediction"] >= self.dai_q_target[0] and nutrition["dai_q_prediction"] <= self.dai_q_target[1]:
            score -= 0
            nutrition["dai_q_variable"] = 0
        elif nutrition["dai_q_prediction"] < self.dai_q_target[0]:
            score -= self.NUTRITION_WEIGHTS["dai_q"] * self._distance(nutrition["dai_q_prediction"], self.dai_q_target[0])
            nutrition["dai_q_variable"] = self._distance(nutrition["dai_q_prediction"], self.dai_q_target[0])
        elif nutrition["dai_q_prediction"] > self.dai_q_target[1]:
            score -= self.NUTRITION_WEIGHTS["dai_q"] * self._distance(nutrition["dai_q_prediction"], self.dai_q_target[1])
            nutrition["dai_q_variable"] = self._distance(nutrition["dai_q_prediction"], self.dai_q_target[1])

        # Dairy serving scoring
        nutrition["dai_s_prediction"] = nutrition.get("dai_s", 0)
        if nutrition["dai_s_prediction"] >= self.dai_s_target[0] and nutrition["dai_s_prediction"] <= self.dai_s_target[1]:
            score -= 0
            nutrition["dai_s_variable"] = 0
        elif nutrition["dai_s_prediction"] < self.dai_s_target[0]:
            score -= self.NUTRITION_WEIGHTS["dai_s"] * self._distance(nutrition["dai_s_prediction"], self.dai_s_target[0])
            nutrition["dai_s_variable"] = self._distance(nutrition["dai_s_prediction"], self.dai_s_target[0])
        elif nutrition["dai_s_prediction"] > self.dai_s_target[1]:
            score -= self.NUTRITION_WEIGHTS["dai_s"] * self._distance(nutrition["dai_s_prediction"], self.dai_s_target[1])
            nutrition["dai_s_variable"] = self._distance(nutrition["dai_s_prediction"], self.dai_s_target[1])

        # Cheese quantity scoring
        nutrition["che_q_prediction"] = nutrition.get("che_q", 0)
        score -= self.NUTRITION_WEIGHTS["che_q"] * self._distance(nutrition["che_q_prediction"], self.che_q_target)
        nutrition["che_q_variable"] = self._distance(nutrition["che_q_prediction"], self.che_q_target)
        
        # Cheese serving scoring
        nutrition["che_s_prediction"] = nutrition.get("che_s", 0)
        score -= self.NUTRITION_WEIGHTS["che_s"] * self._distance(nutrition["che_s_prediction"], self.che_s_target)
        nutrition["che_s_variable"] = self._distance(nutrition["che_s_prediction"], self.che_s_target)

        # Nuts and seeds quantity scoring
        nutrition["nns_q_prediction"] = nutrition.get("nns_q", 0)
        score -= self.NUTRITION_WEIGHTS["nns_q"] * self._distance(nutrition["nns_q_prediction"], self.nns_q_target)
        nutrition["nns_q_variable"] = self._distance(nutrition["nns_q_prediction"], self.nns_q_target)

        # Add meat to nutrition dictionary
        nutrition["mea_q_prediction"] = nutrition.get("mea_q", 0)
        nutrition["mea_q_variable"] = 0
        
        nutrition["mea_s_prediction"] = nutrition.get("mea_s", 0)
        nutrition["mea_s_variable"] = 0

        # Add fish to nutrition dictionary
        nutrition["fis_q_prediction"] = nutrition.get("fis_q", 0)
        nutrition["fis_q_variable"] = 0
        
        nutrition["fis_s_prediction"] = nutrition.get("fis_s", 0)
        nutrition["fis_s_variable"] = 0
        
        # Add oily fish to nutrition dictionary
        nutrition["oif_q_prediction"] = nutrition.get("oif_q", 0)
        nutrition["oif_q_variable"] = 0
        
        nutrition["oif_s_prediction"] = nutrition.get("oif_s", 0)
        nutrition["oif_s_variable"] = 0

        return score

    def process(self, meals):
        """Main processing pipeline"""

        total_combinations = len(meals[0])*len(meals[1])*len(meals[2])*len(meals[3])*len(meals[4])
        print("Total combinations:", total_combinations)
        if total_combinations > self.NUMBER_OF_SAMPLES:
            combinations = self._combinations(0, meals, self.NUMBER_OF_SAMPLES)
        else:
            combinations = self._combinations(0, meals, total_combinations)
        print("Final combinations:", len(combinations))
  
        top_plans = []
        temp_list = []
        
        for idx, combo in enumerate(combinations):            
            meal_ids = [m.id for m in combo]
            nutrition = self.calculate_nutrition(combo)
            score = self.score_daily_meal_plan(nutrition)
            if score == None:
                continue
            temp_list.append(meal_ids)

            # Adjust score based on meal diversity
            penalty = sum(self.meal_counts[m.id] for m in combo) * 0  # Small penalty for repetition
            score -= penalty  # Reduce score if meals repeat
            
            entry = (score, idx, {
                "meals": [m.id for m in combo],
                "score": score,
                "nutrition": nutrition,
            })

            #if all(self.meal_counts[m] < 5 for m in meal_ids):
            if len(top_plans) <= self.TOP_PLANS:
                heapq.heappush(top_plans, entry)
                #self._update_meal_counts(meal_ids, increment=True)
            else:
                if score > top_plans[0][0]:
                    removed = heapq.heappop(top_plans)
                    #self._update_meal_counts(removed[2]["meals"], increment=False)
                    heapq.heappush(top_plans, entry)
                    #self._update_meal_counts(meal_ids, increment=True)

        return sorted([plan[2] for plan in top_plans], key=lambda x: -x["score"])

class WeeklyMealPlanGenerator:
    NUTRITION_WEIGHTS = {
        "energy": 10,
        "protein": 0.08,
        "carb": 0.08,
        "fat": 0.08,
        "fibre": 0.06,
        "calcium": 0.1,
        "iron": 0.1,
        "folate": 0.1,
        "mea_q": 0.1,
        "mea_s": 0.1,
        "blv_q": 0.1,
        "blv_s": 0.1,
        "veg_q": 0.04,
        "veg_s": 0.02,
        "fru_q": 0.04,
        "fru_s": 0.2,
        "jui_s": 1.0,
        "leg_q": 0.06,
        "dai_q": 0.02,
        "dai_s": 0.01,
        "che_q": 0.02,
        "che_s": 0.01,
        "nns_q": 0.06,
        "fis_q": 0.1,
        "fis_s": 0.1,
        "oif_q": 0.1,
        "oif_s": 0.1,
    }

    def __init__(self, results, user_energy_intake):
        self.results = results

        self.sex = "Male"
        self.base_energy_intake = 2500
        print("----->", user_energy_intake)
        self.user_energy_intake = user_energy_intake * 7

        self.meal_counts = defaultdict(int)  # Track meal occurrences in heap

        self.energy_target = self.user_energy_intake * 7
        self.protein_target = [self.user_energy_intake*0.15/4, self.user_energy_intake*0.25/4]
        self.carbs_target = [self.user_energy_intake*0.45/4, self.user_energy_intake*0.6/4]
        self.fats_target = [self.user_energy_intake*0.2/9, self.user_energy_intake*0.35/9]
        self.fibre_target = 25 * 7
        self.calcium_target = 1000 * 7
        self.iron_target = 11 * 7 if self.sex == "Female" else 17 * 7
        self.folate_target = 330 * 7
        self.veg_q_target = self.user_energy_intake*300/self.base_energy_intake * 7
        self.veg_s_target = 3 * 7
        self.fru_q_target = self.user_energy_intake*200/self.base_energy_intake * 7
        self.fru_s_target = 2 * 7
        self.jui_s_target = 1 * 7
        self.leg_q_target = self.user_energy_intake*125/self.base_energy_intake * 7
        self.dai_q_target = [self.user_energy_intake*125/self.base_energy_intake, self.user_energy_intake*250/self.base_energy_intake]
        self.dai_s_target = [1 * 7, 2 * 7]
        self.che_q_target = self.user_energy_intake*25/self.base_energy_intake * 7
        self.che_s_target = 1 * 7
        self.nns_q_target = self.user_energy_intake*30/self.base_energy_intake * 7
        self.mea_q_target = 420
        self.mea_s_target = 3
        self.fis_q_target = 100
        self.fis_s_target = 1
        self.oif_q_target = 100
        self.oif_s_target = 1

    def calculate_nutrition(self, meals):
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
            "leg_s": sum(m['nutrition'].get('leg_s', 0) for m in meals),
            "leg_q": sum(m['nutrition'].get('leg_q', 0) for m in meals),
            "dai_s": sum(m['nutrition'].get('dai_s', 0) for m in meals),
            "dai_q": sum(m['nutrition'].get('dai_q', 0) for m in meals),
            "che_s": sum(m['nutrition'].get('che_s', 0) for m in meals),
            "che_q": sum(m['nutrition'].get('che_q', 0) for m in meals),
            "nns_s": sum(m['nutrition'].get('nns_s', 0) for m in meals),
            "nns_q": sum(m['nutrition'].get('nns_q', 0) for m in meals),
            "fis_q": sum(m['nutrition'].get('fis_q', 0) for m in meals),
            "fis_s": sum(m['nutrition'].get('fis_s', 0) for m in meals),
            "oif_q": sum(m['nutrition'].get('oif_q', 0) for m in meals),
            "oif_s": sum(m['nutrition'].get('oif_s', 0) for m in meals),
        }

        return nutrition_totals

    def _distance(self, prediction, target):
        return abs(prediction - target)/target

    def score_meal_plan(self, nutrition: Dict[str, float]) -> float:
        """Modular scoring system with range checks"""
        
        score = 0.0
        
        # Energy scoring
        nutrition["energy_prediction"] = nutrition.get("energy", 0)
        score -= self.NUTRITION_WEIGHTS["energy"] * self._distance(nutrition["energy_prediction"], self.energy_target)
        nutrition["energy_variable"] = self._distance(nutrition["energy_prediction"], self.energy_target)

        # Protein scoring
        nutrition["protein_prediction"] = nutrition.get("protein", 0)
        if nutrition["protein_prediction"] >= self.protein_target[0] and nutrition["protein_prediction"] <= self.protein_target[1]:
            score -= 0
            nutrition["protein_variable"] = 0
        elif nutrition["protein_prediction"] < self.protein_target[0]:
            score -= self.NUTRITION_WEIGHTS["protein"] * self._distance(nutrition["protein_prediction"], self.protein_target[0])
            nutrition["protein_variable"] = self._distance(nutrition["protein_prediction"], self.protein_target[0])
        elif nutrition["protein_prediction"] > self.protein_target[1]:
            score -= self.NUTRITION_WEIGHTS["protein"] * self._distance(nutrition["protein_prediction"], self.protein_target[1])
            nutrition["protein_variable"] = self._distance(nutrition["protein_prediction"], self.protein_target[1])

        # Carb scoring
        nutrition["carb_prediction"] = nutrition.get("carb", 0)
        if nutrition["carb_prediction"] >= self.carbs_target[0] and nutrition["carb_prediction"] <= self.carbs_target[1]:
            score -= 0
            nutrition["carb_variable"] = 0
        elif nutrition["carb_prediction"] < self.carbs_target[0]:
            score -= self.NUTRITION_WEIGHTS["carb"] * self._distance(nutrition["carb_prediction"], self.carbs_target[0])
            nutrition["carb_variable"] = self._distance(nutrition["carb_prediction"], self.carbs_target[0])
        elif nutrition["carb_prediction"] > self.carbs_target[1]:
            score -= self.NUTRITION_WEIGHTS["carb"] * self._distance(nutrition["carb_prediction"], self.carbs_target[1])
            nutrition["carb_variable"] = self._distance(nutrition["carb_prediction"], self.carbs_target[1])

        # Fats scoring
        nutrition["fat_prediction"] = nutrition.get("fat", 0)
        if nutrition["fat_prediction"] >= self.fats_target[0] and nutrition["fat_prediction"] <= self.fats_target[1]:
            score -= 0
            nutrition["fat_variable"] = 0
        elif nutrition["fat_prediction"] < self.fats_target[0]:
            score -= self.NUTRITION_WEIGHTS["fat"] * self._distance(nutrition["fat_prediction"], self.fats_target[0])
            nutrition["fat_variable"] = self._distance(nutrition["fat_prediction"], self.fats_target[0])
        elif nutrition["fat_prediction"] > self.fats_target[1]:
            score -= self.NUTRITION_WEIGHTS["fat"] * self._distance(nutrition["fat_prediction"], self.fats_target[1])
            nutrition["fat_variable"] = self._distance(nutrition["fat_prediction"], self.fats_target[1])

        # Fibre scoring
        nutrition["fibre_prediction"] = nutrition.get("fibre", 0)
        score -= self.NUTRITION_WEIGHTS["fibre"] * self._distance(nutrition["fibre_prediction"], self.fibre_target)
        nutrition["fibre_variable"] = self._distance(nutrition["fibre_prediction"], self.fibre_target)

        # Calcuim scoring
        nutrition["calcium_prediction"] = nutrition.get("calcium", 0)
        score -= self.NUTRITION_WEIGHTS["calcium"] * self._distance(nutrition["calcium_prediction"], self.calcium_target)
        nutrition["calcium_variable"] = self._distance(nutrition["calcium_prediction"], self.calcium_target)

        # Iron scoring
        nutrition["iron_prediction"] = nutrition.get("iron", 0)
        score -= self.NUTRITION_WEIGHTS["iron"] * self._distance(nutrition["iron_prediction"], self.iron_target)
        nutrition["iron_variable"] = self._distance(nutrition["iron_prediction"], self.iron_target)

        # Folate scoring
        nutrition["folate_prediction"] = nutrition.get("folate", 0)
        score -= self.NUTRITION_WEIGHTS["folate"] * self._distance(nutrition["folate_prediction"], self.folate_target)
        nutrition["folate_variable"] = self._distance(nutrition["folate_prediction"], self.folate_target)

        # Vegetable quantity scoring
        nutrition["veg_q_prediction"] = nutrition.get("veg_q", 0)
        score -= self.NUTRITION_WEIGHTS["veg_q"] * self._distance(nutrition["veg_q_prediction"], self.veg_q_target)
        nutrition["veg_q_variable"] = self._distance(nutrition["veg_q_prediction"], self.veg_q_target)

        # Vegetable serving scoring
        nutrition["veg_s_prediction"] = nutrition.get("veg_s", 0)
        score -= self.NUTRITION_WEIGHTS["veg_s"] * self._distance(nutrition["veg_s_prediction"], self.veg_s_target)
        nutrition["veg_s_variable"] = self._distance(nutrition["veg_s_prediction"], self.veg_s_target)

        # Fruit quantity scoring
        nutrition["fru_q_prediction"] = nutrition.get("fru_q", 0)
        score -= self.NUTRITION_WEIGHTS["fru_q"] * self._distance(nutrition["fru_q_prediction"], self.fru_q_target)
        nutrition["fru_q_variable"] = self._distance(nutrition["fru_q_prediction"], self.fru_q_target)
        
        # Fruit serving scoring
        nutrition["fru_s_prediction"] = nutrition.get("fru_s", 0)
        score -= self.NUTRITION_WEIGHTS["fru_s"] * self._distance(nutrition["fru_s_prediction"], self.fru_s_target)
        nutrition["fru_s_variable"] = self._distance(nutrition["fru_s_prediction"], self.fru_s_target)

        # Juice serving scoring
        nutrition["jui_s_prediction"] = nutrition.get("jui_s", 0)
        score -= self.NUTRITION_WEIGHTS["jui_s"] * self._distance(nutrition["jui_s_prediction"], self.jui_s_target)
        nutrition["jui_s_variable"] = self._distance(nutrition["jui_s_prediction"], self.jui_s_target)


        # Plant protein quantity scoring
        nutrition["leg_q_prediction"] = nutrition.get("leg_q", 0)
        score -= self.NUTRITION_WEIGHTS["leg_q"] * self._distance(nutrition["leg_q_prediction"], self.leg_q_target)
        nutrition["leg_q_variable"] = self._distance(nutrition["leg_q_prediction"], self.leg_q_target)

        # Dairy quantity scoring
        nutrition["dai_q_variable"] = 0
        nutrition["dai_q_prediction"] = nutrition.get("dai_q", 0)
        if nutrition["dai_q_prediction"] >= self.dai_q_target[0] and nutrition["dai_q_prediction"] <= self.dai_q_target[1]:
            score -= 0
            nutrition["dai_q_variable"] = 0
        elif nutrition["dai_q_prediction"] < self.dai_q_target[0]:
            score -= self.NUTRITION_WEIGHTS["dai_q"] * self._distance(nutrition["dai_q_prediction"], self.dai_q_target[0])
            nutrition["dai_q_variable"] = self._distance(nutrition["dai_q_prediction"], self.dai_q_target[0])
        elif nutrition["dai_q_prediction"] > self.dai_q_target[1]:
            score -= self.NUTRITION_WEIGHTS["dai_q"] * self._distance(nutrition["dai_q_prediction"], self.dai_q_target[1])
            nutrition["dai_q_variable"] = self._distance(nutrition["dai_q_prediction"], self.dai_q_target[1])

        # Dairy serving scoring
        nutrition["dai_s_prediction"] = nutrition.get("dai_s", 0)
        if nutrition["dai_s_prediction"] >= self.dai_s_target[0] and nutrition["dai_s_prediction"] <= self.dai_s_target[1]:
            score -= 0
            nutrition["dai_s_variable"] = 0
        elif nutrition["dai_s_prediction"] < self.dai_s_target[0]:
            score -= self.NUTRITION_WEIGHTS["dai_s"] * self._distance(nutrition["dai_s_prediction"], self.dai_s_target[0])
            nutrition["dai_s_variable"] = self._distance(nutrition["dai_s_prediction"], self.dai_s_target[0])
        elif nutrition["dai_s_prediction"] > self.dai_s_target[1]:
            score -= self.NUTRITION_WEIGHTS["dai_s"] * self._distance(nutrition["dai_s_prediction"], self.dai_s_target[1])
            nutrition["dai_s_variable"] = self._distance(nutrition["dai_s_prediction"], self.dai_s_target[1])

        # Cheese quantity scoring
        nutrition["che_q_prediction"] = nutrition.get("che_q", 0)
        score -= self.NUTRITION_WEIGHTS["che_q"] * self._distance(nutrition["che_q_prediction"], self.che_q_target)
        nutrition["che_q_variable"] = self._distance(nutrition["che_q_prediction"], self.che_q_target)
        
        # Cheese serving scoring
        nutrition["che_s_prediction"] = nutrition.get("che_s", 0)
        score -= self.NUTRITION_WEIGHTS["che_s"] * self._distance(nutrition["che_s_prediction"], self.che_s_target)
        nutrition["che_s_variable"] = self._distance(nutrition["che_s_prediction"], self.che_s_target)

        # Nuts and seeds quantity scoring
        nutrition["nns_q_prediction"] = nutrition.get("nns_q", 0)
        score -= self.NUTRITION_WEIGHTS["nns_q"] * self._distance(nutrition["nns_q_prediction"], self.nns_q_target)
        nutrition["nns_q_variable"] = self._distance(nutrition["nns_q_prediction"], self.nns_q_target)

        # Meat quantity scoring
        nutrition["mea_q_prediction"] = nutrition.get("mea_q", 0)
        score -= self.NUTRITION_WEIGHTS["mea_q"] * self._distance(nutrition["mea_q_prediction"], self.mea_q_target)
        nutrition["mea_q_variable"] = self._distance(nutrition["mea_q_prediction"], self.mea_q_target)

        # Meat serving scoring
        nutrition["mea_s_prediction"] = nutrition.get("mea_s", 0)
        score -= self.NUTRITION_WEIGHTS["mea_s"] * self._distance(nutrition["mea_s_prediction"], self.mea_s_target)
        nutrition["mea_s_variable"] = self._distance(nutrition["mea_s_prediction"], self.mea_s_target)

        # Fish quantity scoring
        nutrition["fis_q_prediction"] = nutrition.get("fis_q", 0)
        score -= self.NUTRITION_WEIGHTS["fis_q"] * self._distance(nutrition["fis_q_prediction"], self.fis_q_target)
        nutrition["fis_q_variable"] = self._distance(nutrition["fis_q_prediction"], self.fis_q_target)
        
        # Fish serving scoring
        nutrition["fis_s_prediction"] = nutrition.get("fis_s", 0)
        score -= self.NUTRITION_WEIGHTS["fis_s"] * self._distance(nutrition["fis_s_prediction"], self.fis_s_target)
        nutrition["fis_s_variable"] = self._distance(nutrition["fis_s_prediction"], self.fis_s_target)

        # Oily fish quantity scoring
        nutrition["oif_q_prediction"] = nutrition.get("oif_q", 0)
        score -= self.NUTRITION_WEIGHTS["oif_q"] * self._distance(nutrition["oif_q_prediction"], self.oif_q_target)
        nutrition["oif_q_variable"] = self._distance(nutrition["oif_q_prediction"], self.oif_q_target)
        
        # Oily fish serving scoring
        nutrition["oif_s_prediction"] = nutrition.get("oif_s", 0)
        score -= self.NUTRITION_WEIGHTS["oif_s"] * self._distance(nutrition["oif_s_prediction"], self.oif_s_target)
        nutrition["oif_s_variable"] = self._distance(nutrition["oif_s_prediction"], self.oif_s_target)

        return score

    def _combinations(self):
        """Generate meal combinations with smart sampling"""
        return combinations(self.results, 7)

    def _update_meal_counts(self, meal_ids: List[int], increment: bool):
        """NEW: Properly handle meal count updates"""
        delta = 1 if increment else -1
        for i, m in enumerate(meal_ids):
            if i in [5*x + offset for x in range(7) for offset in [0, 2, 4]]:  # Only track main meals
                self.meal_counts[m] += delta

    def process(self) -> List[Dict]:
        """Main processing pipeline"""
        top_plans = []
        combinations = self._combinations()

        for idx, combo in enumerate(combinations):
            meal_ids = [mid for np in combo for mid in np['meals']]
            #meal_ids = [m.id for m in combo]
            nutrition = self.calculate_nutrition(combo)
            score = self.score_meal_plan(nutrition)

            # Adjust score based on meal diversity
            if idx == 0:
                self._update_meal_counts(meal_ids, increment=True)

            penalty = sum(self.meal_counts[mid] for np in combo for mid in np['meals']) * 0.1  # Small penalty for repetition
            score -= penalty  # Reduce score if meals repeat
            
            entry = (score, idx, {
                "meals": [m['meals'] for m in combo],
                "score": score,
                "nutrition": nutrition,
            })

            #if all(self.meal_counts[m] < 3 for m in meal_ids):
            if len(top_plans) <= TOP_PLANS:
                heapq.heappush(top_plans, entry)
                #self._update_meal_counts(meal_ids, increment=True)
            else:
                if score > top_plans[0][0]:
                    removed = heapq.heappop(top_plans)
                    #self._update_meal_counts(removed[2]["meals"], increment=False)
                    heapq.heappush(top_plans, entry)
                    #self._update_meal_counts(meal_ids, increment=True)

        return sorted([plan[2] for plan in top_plans], key=lambda x: -x["score"])

class Command(BaseCommand):
    help = 'Generate personalized daily meal plans'
    
    def handle(self, *args, **kwargs):
        daily_generator = DailyMealPlanGenerator()
        meals = daily_generator._filtering()
        print(len(meals))
        meals = daily_generator._get_five_meals(meals)
        print("Breakfasts:", len(meals[0]))
        print("Morning Snacks:", len(meals[1]))
        print("Lunches:", len(meals[2]))
        print("Afternoon Snack:", len(meals[3]))
        print("Dinners:", len(meals[4]))
        
        daily_results = daily_generator.process(meals)
        print("------------------------------------")
        print("energy", daily_generator.energy_target)
        print("protein", daily_generator.protein_target)
        print("carbs", daily_generator.carbs_target)
        print("fats", daily_generator.fats_target)
        print("fibre", daily_generator.fibre_target)
        print("calcium", daily_generator.calcium_target)
        print("iron", daily_generator.iron_target)
        print("folate", daily_generator.folate_target)
        print("veg_q", daily_generator.veg_q_target)
        print("veg_s", daily_generator.veg_s_target)
        print("fru_q", daily_generator.fru_q_target)
        print("fru_s", daily_generator.fru_s_target)
        print("jui_s", daily_generator.jui_s_target)
        print("leg_q", daily_generator.leg_q_target)
        print("dai_q", daily_generator.dai_q_target)
        print("dai_s", daily_generator.dai_s_target)
        print("che_q", daily_generator.che_q_target)
        print("che_s", daily_generator.che_s_target)
        print("nns_q", daily_generator.nns_q_target)
        print("mea_q", daily_generator.mea_q_target)
        print("mea_s", daily_generator.mea_s_target)
        print("fis_q", daily_generator.fis_q_target)
        print("fis_s", daily_generator.fis_s_target)
        print("oif_q", daily_generator.oif_q_target)
        print("oif_s", daily_generator.oif_s_target)
        self.daily_dataframe_transform(daily_results)


        print("----->", daily_generator.user_energy_intake)

        weekly_generator = WeeklyMealPlanGenerator(daily_results, daily_generator.user_energy_intake)
        weekly_results = weekly_generator.process()
        print("------------------------------------")
        print("energy", weekly_generator.energy_target)
        print("protein", weekly_generator.protein_target)
        print("carbs", weekly_generator.carbs_target)
        print("fats", weekly_generator.fats_target)
        print("fibre", weekly_generator.fibre_target)
        print("calcium", weekly_generator.calcium_target)
        print("iron", weekly_generator.iron_target)
        print("folate", weekly_generator.folate_target)
        print("veg_q", weekly_generator.veg_q_target)
        print("veg_s", weekly_generator.veg_s_target)
        print("fru_q", weekly_generator.fru_q_target)
        print("fru_s", weekly_generator.fru_s_target)
        print("jui_s", weekly_generator.jui_s_target)
        print("leg_q", weekly_generator.leg_q_target)
        print("dai_q", weekly_generator.dai_q_target)
        print("dai_s", weekly_generator.dai_s_target)
        print("che_q", weekly_generator.che_q_target)
        print("che_s", weekly_generator.che_s_target)
        print("nns_q", weekly_generator.nns_q_target)
        print("mea_q", weekly_generator.mea_q_target)
        print("mea_s", weekly_generator.mea_s_target)
        print("fis_q", weekly_generator.fis_q_target)
        print("fis_s", weekly_generator.fis_s_target)
        print("oif_q", weekly_generator.oif_q_target)
        print("oif_s", weekly_generator.oif_s_target)

        self.weekly_dataframe_transform(weekly_results)
        self.print_best_week(weekly_results[0])

    def print_best_week(self, result):
        # Define day labels
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Define meal labels (optional)
        meal_labels = ["Breakfast", "Snack_1", "Lunch", "Snack_2", "Dinner"]

        # Create DataFrame
        df = pd.DataFrame(result['meals'], index=days_of_week, columns=meal_labels).T

        # Display DataFrame
        print(df)

    def weekly_dataframe_transform(self, results):
        """Transform the results into a dataframe"""

        meal_plans_list = []
        print("------------------------------------------------------------------------------------------------------------------------------")
        for plan in results:
            meal_plans_list.append({
                "Score": plan['score'],
                "Ene_v": plan['nutrition']['energy_variable'],
                "Ene_p": float(plan['nutrition']['energy_prediction']),
                "Pro_v": plan['nutrition']['protein_variable'],
                "Pro_p": float(plan['nutrition']['protein_prediction']),
                "Car_v": plan['nutrition']['carb_variable'],
                "Car_p": float(plan['nutrition']['carb_prediction']),
                "Fat_v": plan['nutrition']['fat_variable'],
                "Fat_p": float(plan['nutrition']['fat_prediction']),
                "Fib_v": plan['nutrition']['fibre_variable'],
                "Fib_p": float(plan['nutrition']['fibre_prediction']),
                "Cal_v": plan['nutrition']['calcium_variable'],
                "Cal_p": float(plan['nutrition']['calcium_prediction']),
                "Iro_v": plan['nutrition']['iron_variable'],
                "Iro_p": float(plan['nutrition']['iron_prediction']),
                "Fol_v": plan['nutrition']['folate_variable'],
                "Fol_p": float(plan['nutrition']['folate_prediction']),
                "Veg_q_v": plan['nutrition']['veg_q_variable'],
                "Veg_q_p": float(plan['nutrition']['veg_q_prediction']),
                "Veg_s_v": plan['nutrition']['veg_s_variable'],
                "Veg_s_p": float(plan['nutrition']['veg_s_prediction']),
                "Fru_q_v": plan['nutrition']['fru_q_variable'],
                "Fru_q_p": float(plan['nutrition']['fru_q_prediction']),
                "Fru_s_v": plan['nutrition']['fru_s_variable'],
                "Fru_s_p": float(plan['nutrition']['fru_s_prediction']),
                "Jui_s_v": plan['nutrition']['jui_s_variable'],
                "Jui_s_p": float(plan['nutrition']['jui_s_prediction']),
                "Leg_q_v": plan['nutrition']['leg_q_variable'],
                "Leg_q_p": float(plan['nutrition']['leg_q_prediction']),
                "Dai_q_v": plan['nutrition']['dai_q_variable'],
                "Dai_q_p": float(plan['nutrition']['dai_q_prediction']),
                "Dai_s_v": plan['nutrition']['dai_s_variable'],
                "Dai_s_p": float(plan['nutrition']['dai_s_prediction']),
                "Che_q_v": plan['nutrition']['che_q_variable'],
                "Che_q_p": float(plan['nutrition']['che_q_prediction']),
                "Che_s_v": plan['nutrition']['che_s_variable'],
                "Che_s_p": float(plan['nutrition']['che_s_prediction']),
                "Nns_q_v": plan['nutrition']['nns_q_variable'],
                "Nns_q_p": float(plan['nutrition']['nns_q_prediction']),
                "Mea_q_v": plan['nutrition']['mea_q_variable'],
                "Mea_q_p": float(plan['nutrition']['mea_q_prediction']),
                "Mea_s_v": plan['nutrition']['mea_s_variable'],
                "Mea_s_p": float(plan['nutrition']['mea_s_prediction']),
                "Fis_q_v": plan['nutrition']['fis_q_variable'],
                "Fis_q_p": float(plan['nutrition']['fis_q_prediction']),
                "Fis_s_v": plan['nutrition']['fis_s_variable'],
                "Fis_s_p": float(plan['nutrition']['fis_s_prediction']),
                "Oif_q_v": plan['nutrition']['oif_s_variable'],
                "Oif_q_p": float(plan['nutrition']['oif_s_prediction']),
                "Oif_s_v": plan['nutrition']['oif_s_variable'],
                "Oif_s_p": float(plan['nutrition']['oif_s_prediction']),
            })
        # Convert collected data into a DataFrame
        df = pd.DataFrame(meal_plans_list)

        # Print DataFrame
        print(df)

    def daily_dataframe_transform(self, results):
        """Transform the results into a dataframe"""

        # Collect all meal plans in a list
        meal_plans_list = []

        #for idx, plan in enumerate(results, 1):
        print("------------------------------------------------------------------------------------------------------------------------------")
        # Iterate through top meal plans
        for plan in results:
            meal_plans_list.append({
                "Score": plan['score'],
                "Ene_v": plan['nutrition']['energy_variable'],
                "Ene_p": float(plan['nutrition']['energy_prediction']),
                "Pro_v": plan['nutrition']['protein_variable'],
                "Pro_p": float(plan['nutrition']['protein_prediction']),
                "Car_v": plan['nutrition']['carb_variable'],
                "Car_p": float(plan['nutrition']['carb_prediction']),
                "Fat_v": plan['nutrition']['fat_variable'],
                "Fat_p": float(plan['nutrition']['fat_prediction']),
                "Fib_v": plan['nutrition']['fibre_variable'],
                "Fib_p": float(plan['nutrition']['fibre_prediction']),
                "Cal_v": plan['nutrition']['calcium_variable'],
                "Cal_p": float(plan['nutrition']['calcium_prediction']),
                "Iro_v": plan['nutrition']['iron_variable'],
                "Iro_p": float(plan['nutrition']['iron_prediction']),
                "Fol_v": plan['nutrition']['folate_variable'],
                "Fol_p": float(plan['nutrition']['folate_prediction']),
                "Veg_q_v": plan['nutrition']['veg_q_variable'],
                "Veg_q_p": float(plan['nutrition']['veg_q_prediction']),
                "Veg_s_v": plan['nutrition']['veg_s_variable'],
                "Veg_s_p": float(plan['nutrition']['veg_s_prediction']),
                "Fru_q_v": plan['nutrition']['fru_q_variable'],
                "Fru_q_p": float(plan['nutrition']['fru_q_prediction']),
                "Fru_s_v": plan['nutrition']['fru_s_variable'],
                "Fru_s_p": float(plan['nutrition']['fru_s_prediction']),
                "Jui_s_v": plan['nutrition']['jui_s_variable'],
                "Jui_s_p": float(plan['nutrition']['jui_s_prediction']),
                "Leg_q_v": plan['nutrition']['leg_q_variable'],
                "Leg_q_p": float(plan['nutrition']['leg_q_prediction']),
                "Dai_q_v": plan['nutrition']['dai_q_variable'],
                "Dai_q_p": float(plan['nutrition']['dai_q_prediction']),
                "Dai_s_v": plan['nutrition']['dai_s_variable'],
                "Dai_s_p": float(plan['nutrition']['dai_s_prediction']),
                "Che_q_v": plan['nutrition']['che_q_variable'],
                "Che_q_p": float(plan['nutrition']['che_q_prediction']),
                "Che_s_v": plan['nutrition']['che_s_variable'],
                "Che_s_p": float(plan['nutrition']['che_s_prediction']),
                "Nns_q_v": plan['nutrition']['nns_q_variable'],
                "Nns_q_p": float(plan['nutrition']['nns_q_prediction']),
                
                "Mea_q_v": plan['nutrition']['mea_q_variable'],
                "Mea_q_p": float(plan['nutrition']['mea_q_prediction']),
                "Mea_s_v": plan['nutrition']['mea_s_variable'],
                "Mea_s_p": float(plan['nutrition']['mea_s_prediction']),
                "Fis_q_v": plan['nutrition']['fis_q_variable'],
                "Fis_q_p": float(plan['nutrition']['fis_q_prediction']),
                "Fis_s_v": plan['nutrition']['fis_s_variable'],
                "Fis_s_p": float(plan['nutrition']['fis_s_prediction']),
                "Oif_q_v": plan['nutrition']['oif_q_variable'],
                "Oif_q_p": float(plan['nutrition']['oif_q_prediction']),
                "Oif_s_v": plan['nutrition']['oif_s_variable'],
                "Oif_s_p": float(plan['nutrition']['oif_s_prediction']),
            })
        # Set the float format to 3 decimal places
        pd.options.display.float_format = '{:.3f}'.format

        # Convert collected data into a DataFrame
        df = pd.DataFrame(meal_plans_list)

        # Print DataFrame
        print(df)
            