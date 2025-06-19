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
NUTRIENT_TOLERANCE = 0.1  # 10% tolerance for most nutrients
SAMPLE_SIZE = 10

class DailyMealPlanGenerator:
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
        "oif_q": 0.1,
        "oif_s": 0.1,
    }

    MEAL_TYPES = [
        "Breakfast",
        "Morning Snack",
        "Lunch",
        "Afternoon Snack",
        "Dinner"
    ]

    def __init__(self):
        self.sex = "Male"
        self.user_weight = 80
        self.user_energy_intake = 2500
        self.user_preference = "omnivore"
        self.user_allergy = "none"
        self.cuisine = ["Irish"]
        
        self.NUMBER_OF_SAMPLES = 200000
        self.TOP_PLANS = 20
        
        self.meal_counts = defaultdict(int)
        
        self.energy_target = self.user_energy_intake
        self.protein_target = [self.user_energy_intake * 0.15/4, self.user_energy_intake * 0.25/4]
        self.carbs_target = [self.user_energy_intake * 0.45/8, self.user_energy_intake * 0.6/8]
        self.fats_target = [self.user_energy_intake * 0.2/9, self.user_energy_intake * 0.35/8]
        self.fibre_target = 25
        self.calcium = 1000
        self.iron = 11 if self.sex == "Female" else 17
        self.folate = 330
        self.veg_q_target = self.user_energy_intake*300/2500
        self.veg_s_target = 3
        self.fru_q_target = self.user_energy_intake*200/2500
        self.fru_s_target = 2
        self.jui_s_target = 1
        self.leg_q_target = self.user_energy_intake*125/2500
        self.dai_q_target = [self.user_energy_intake*125/2500, self.user_energy_intake*250/2500]
        self.dai_s_target = [1, 2]
        self.che_q_target = self.user_energy_intake*25/2500
        self.che_s_target = 1
        self.nns_q_target = self.user_energy_intake*30/2500

        self.energy_counter = 0
        self.protein_counter = 0
        self.carbs_counter = 0
        self.fibre_counter = 0
        self.fats_counter = 0
        self.calcium_counter = 0
        self.iron_counter = 0
        self.folate_counter = 0
        self.veg_q_counter = 0
        self.veg_s_counter = 0
        self.fru_q_counter = 0
        self.fru_s_counter = 0
        self.jui_s_counter = 0
        self.leg_q_counter = 0
        self.dai_q_counter = 0
        self.dai_s_counter = 0
        self.che_q_counter = 0
        self.che_s_counter = 0
        self.nns_q_counter = 0

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

    def _combinations(self, flag, results, sets, num_samples):
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
            # "energy_variable": -1,
            # "protein_variable": -1,
            # "carb_variable": -1,
            # "fat_variable": -1,
            # "fibre_variable": -1,
            # "calcium_variable": -1,
            # "iron_variable": -1,
            # "folate_variable": -1,
            # "veg_q_variable": -1,
            # "veg_s_variable": -1,
            # "fru_q_variable": -1,
            # "fru_s_variable": -1,
            # "jui_s_variable": -1,
            # "plp_q_variable": -1,
            # "dai_q_variable": -1,
            # "dai_s_variable": -1,
            # "che_q_variable": -1,
            # "che_s_variable": -1,
            # "nns_q_variable": -1,
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

    def score_daily_meal_plan(self, nutrition):
        """Modular scoring system with range checks"""
        
        score = 0.0
        
        # Energy scoring
        nutrition["energy_variable"] = 0
        nutrition["energy_prediction"] = nutrition.get("energy", 0)
        if nutrition["energy_prediction"] >= self.user_energy_intake*0.95 and nutrition["energy_prediction"] <= self.user_energy_intake*1.05:
            score += 10 * self.NUTRITION_WEIGHTS["energy"]
            nutrition["energy_variable"] = 10
        elif nutrition["energy_prediction"] >= self.user_energy_intake*0.9 and nutrition["energy_prediction"] <= self.user_energy_intake*1.1:
            score += 5 * self.NUTRITION_WEIGHTS["energy"]
            nutrition["energy_variable"] = 5
        elif nutrition["energy_prediction"] >= self.user_energy_intake*0.85 and nutrition["energy_prediction"] <= self.user_energy_intake*1.15:
            score += 0 * self.NUTRITION_WEIGHTS["energy"]
            nutrition["energy_variable"] = 5
        # elif nutrition["energy_prediction"] < self.user_energy_intake*0.85 or nutrition["energy_prediction"] > self.user_energy_intake*1.15:
        #     #print("energy ouside +-15%")
        #     self.energy_counter += 1
        #     return None

        # Protein scoring
        protein_target = [self.user_energy_intake * 0.15/4, self.user_energy_intake * 0.25/4]
        nutrition["protein_variable"] = 0
        nutrition["protein_prediction"] = nutrition.get("protein", 0)
        if nutrition["protein_prediction"] >= self.user_energy_intake*0.15/4 and nutrition["protein_prediction"] <= self.user_energy_intake*0.25/4:
            score += 10 * self.NUTRITION_WEIGHTS["protein"]
            nutrition["protein_variable"] = 10
        elif nutrition["protein_prediction"] >= self.user_energy_intake*0.12/4 and nutrition["protein_prediction"] <= self.user_energy_intake*0.28/4:
            score += 0 * self.NUTRITION_WEIGHTS["protein"]
            nutrition["protein_variable"] = 0
        # elif nutrition["protein_prediction"] < self.user_energy_intake*0.12/4 or nutrition["protein_prediction"] > self.user_energy_intake*0.28/4:
        #     #print("protein ouside 15-25%")
        #     self.protein_counter += 1
        #     return None

        # Carb scoring
        carbs_target = [self.user_energy_intake * 0.45/8, self.user_energy_intake * 0.6/8]
        nutrition["carb_variable"] = 0
        nutrition["carb_prediction"] = nutrition.get("carb", 0)
        if nutrition["carb_prediction"] >= self.user_energy_intake*0.45/8 and nutrition["carb_prediction"] <= self.user_energy_intake * 0.6/8:
            score += 10 * self.NUTRITION_WEIGHTS["carb"]
            nutrition["carb_variable"] = 10
        elif nutrition["carb_prediction"] >= self.user_energy_intake*0.37/8 and nutrition["carb_prediction"] <= self.user_energy_intake * 0.68/8:
            score += 0 * self.NUTRITION_WEIGHTS["carb"]
            nutrition["carb_variable"] = 0
        # elif nutrition["carb_prediction"] < self.user_energy_intake*0.37/8 or nutrition["carb_prediction"] > self.user_energy_intake * 0.68/8:
        #     #print("carbs ouside 45-60%")
        #     self.carbs_counter += 1
        #     return None

        # Fats scoring
        fats_target = [self.user_energy_intake * 0.2/9, self.user_energy_intake * 0.35/8]
        nutrition["fat_variable"] = 0
        nutrition["fat_prediction"] = nutrition.get("fat", 0)
        if nutrition["fat_prediction"] >= self.user_energy_intake*0.2/9 and nutrition["fat_prediction"] <= self.user_energy_intake*0.35/9:
            score += 10 * self.NUTRITION_WEIGHTS["fat"]
            nutrition["fat_variable"] = 10
        elif nutrition["fat_prediction"] >= self.user_energy_intake*0.16/9 and nutrition["fat_prediction"] <= self.user_energy_intake*0.39/9:
            score += 0 * self.NUTRITION_WEIGHTS["fat"]
            nutrition["fat_variable"] = 0
        # elif nutrition["fat_prediction"] < self.user_energy_intake*0.16/9 or nutrition["fat_prediction"] > self.user_energy_intake*0.39/9:
        #     #print("carbs ouside 20-35%")
        #     self.fats_counter += 1
        #     return None

        # Fibre scoring
        fibre_target = 25
        nutrition["fibre_variable"] = 0
        nutrition["fibre_prediction"] = nutrition.get("fibre", 0)
        if nutrition["fibre_prediction"] > fibre_target*0.9:
            score += 10 * self.NUTRITION_WEIGHTS["fibre"]
            nutrition["fibre_variable"] = 10
        elif nutrition["fibre_prediction"] > fibre_target*0.8:
            score += 5 * self.NUTRITION_WEIGHTS["fibre"]
            nutrition["fibre_variable"] = 5
        elif nutrition["fibre_prediction"] > fibre_target*0.7:
            score += 0 * self.NUTRITION_WEIGHTS["fibre"]
            nutrition["fibre_variable"] = 0
        # elif nutrition["fibre_prediction"] < fibre_target*0.7:
        #     #print("fibres under ", fibre_target*0.13)
        #     self.fibre_counter += 1
        #     return None

        # Calcuim scoring
        calcium_target = 1000
        nutrition["calcium_variable"] = 0
        nutrition["calcium_prediction"] = nutrition.get("calcium", 0)
        if nutrition["calcium_prediction"] >= calcium_target*0.95 and nutrition["calcium_prediction"] <= calcium_target*1.05:
            score += 10 * self.NUTRITION_WEIGHTS["calcium"]
            nutrition["calcium_variable"] = 10
        elif nutrition["calcium_prediction"] >= calcium_target*0.9 and nutrition["calcium_prediction"] <= calcium_target*1.1:
            score += 5 * self.NUTRITION_WEIGHTS["calcium"]
            nutrition["calcium_variable"] = 5
        elif nutrition["calcium_prediction"] >= calcium_target*0.85 and nutrition["calcium_prediction"] <= calcium_target*1.15:
            score += 0 * self.NUTRITION_WEIGHTS["calcium"]
            nutrition["calcium_variable"] = 0
        # elif nutrition["calcium_prediction"] < calcium_target*0.85 or nutrition["calcium_prediction"] > calcium_target*1.15:
        #     #print("calcium outside +-15%")
        #     self.calcium_counter += 1
        #     return None

        # Iron scoring
        if self.sex == 'Male':
            iron_target = 11
        elif self.sex == 'Female':
            iron_target = 17
        nutrition["iron_variable"] = 0
        nutrition["iron_prediction"] = nutrition.get("iron", 0)
        if nutrition["iron_prediction"] >= iron_target*0.95 and nutrition["iron_prediction"] <= iron_target*1.05:
            score += 10 * self.NUTRITION_WEIGHTS["iron"]
            nutrition["iron_variable"] = 10
        elif nutrition["iron_prediction"] >= iron_target*0.9 and nutrition["iron_prediction"] <= iron_target*1.1:
            score += 5 * self.NUTRITION_WEIGHTS["iron"]
            nutrition["iron_variable"] = 5
        elif nutrition["iron_prediction"] >= iron_target*0.85 and nutrition["iron_prediction"] <= iron_target*1.15:
            score += 0 * self.NUTRITION_WEIGHTS["iron"]
            nutrition["iron_variable"] = 0
        # elif nutrition["iron_prediction"] < iron_target*0.85 or nutrition["iron_prediction"] > iron_target*1.15:
        #     #print("iron outside +-15%")
        #     self.iron_counter += 1
        #     return None

        # Folate scoring
        folate_target = 330
        nutrition["folate_variable"] = 0
        nutrition["folate_prediction"] = nutrition.get("folate", 0)
        if nutrition["folate_prediction"] >= folate_target*0.95 and nutrition["folate_prediction"] <= folate_target*1.05:
            score += 10 * self.NUTRITION_WEIGHTS["folate"]
            nutrition["folate_variable"] = 10
        elif nutrition["folate_prediction"] >= folate_target*0.9 and nutrition["folate_prediction"] <= folate_target*1.1:
            score += 5 * self.NUTRITION_WEIGHTS["folate"]
            nutrition["folate_variable"] = 5
        elif nutrition["folate_prediction"] >= folate_target*0.85 and nutrition["folate_prediction"] <= folate_target*1.15:
            score += 0 * self.NUTRITION_WEIGHTS["folate"]
            nutrition["folate_variable"] = 0
        # elif nutrition["folate_prediction"] < folate_target*0.85 or nutrition["folate_prediction"] > folate_target*1.15:
        #     #print("folate outside +-15%")
        #     self.folate_counter += 1
        #     return None

        # Vegetable quantity scoring
        veg_q_target = self.user_energy_intake*300/2500
        nutrition["veg_q_variable"] = 0
        nutrition["veg_q_prediction"] = nutrition.get("veg_q", 0)
        if nutrition["veg_q_prediction"] > veg_q_target*0.9:
            score += 10 * self.NUTRITION_WEIGHTS["veg_q"]
            nutrition["veg_q_variable"] = 10
        elif nutrition["veg_q_prediction"] > veg_q_target*0.8:
            score += 5 * self.NUTRITION_WEIGHTS["veg_q"]
            nutrition["veg_q_variable"] = 5
        elif nutrition["veg_q_prediction"] > veg_q_target*0.7:
            score += 0 * self.NUTRITION_WEIGHTS["veg_q"]
            nutrition["veg_q_variable"] = 0
        # elif nutrition["veg_q_prediction"] < veg_q_target*0.7:
        #     #print("vegetables quantity less than", veg_q_target*0.3)
        #     self.veg_q_counter += 1
        #     return None

        # Vegetable serving scoring
        veg_s_target = 3
        nutrition["veg_s_variable"] = 0
        nutrition["veg_s_prediction"] = nutrition.get("veg_s", 0)
        if nutrition["veg_s_prediction"] > 2:
            score += 10 * self.NUTRITION_WEIGHTS["veg_s"]
            nutrition["veg_s_variable"] = 10
        elif nutrition["veg_s_prediction"] > 1:
            score += 5 * self.NUTRITION_WEIGHTS["veg_s"]
            nutrition["veg_s_variable"] = 5
        elif nutrition["veg_s_prediction"] > 0:
            score += 0 * self.NUTRITION_WEIGHTS["veg_s"]
            nutrition["veg_s_variable"] = 0
        # elif nutrition["veg_s_prediction"] == 0:
        #     #print("vegetables servings less than 0")
        #     self.veg_s_counter += 1
        #     return None

        # Fruit quantity scoring
        fry_q_target = self.user_energy_intake*200/2500
        fruit_quantity_variable = 0
        fruit_quantity_target = 200
        nutrition["fru_q_variable"] = 0
        nutrition["fru_q_prediction"] = nutrition.get("fru_q", 0)
        if nutrition["fru_q_prediction"] >= fry_q_target*0.95 and nutrition["fru_q_prediction"] >= fry_q_target*1.05:
            score += 10 * self.NUTRITION_WEIGHTS["fru_q"]
            nutrition["fru_q_variable"] = 10
        elif nutrition["fru_q_prediction"] >= fry_q_target*0.9 and nutrition["fru_q_prediction"] >= fry_q_target*1.1:
            score += 5 * self.NUTRITION_WEIGHTS["fru_q"]
            nutrition["fru_q_variable"] = 5
        elif nutrition["fru_q_prediction"] >= fry_q_target*0.85 and nutrition["fru_q_prediction"] >= fry_q_target*1.15:
            score += 0 * self.NUTRITION_WEIGHTS["fru_q"]
            nutrition["fru_q_variable"] = 0
        # elif nutrition["fru_q_prediction"] < fry_q_target*0.85 or nutrition["fru_q_prediction"] > fry_q_target*1.15:
        #     #print("fruits quantity outside +-15%")
        #     self.fru_q_counter += 1
        #     return None
        
        # Fruit serving scoring
        fruit_serving_target = 2
        nutrition["fru_s_variable"] = 0
        nutrition["fru_s_prediction"] = nutrition.get("fru_s", 0)
        if nutrition["fru_s_prediction"] == fruit_serving_target:
            score += 10 * self.NUTRITION_WEIGHTS["fru_s"]
            nutrition["fru_s_variable"] = 10
        elif fruit_serving_target-1 <= nutrition["fru_s_prediction"] <= fruit_serving_target+1:
            score += 5 * self.NUTRITION_WEIGHTS["fru_s"]
            nutrition["fru_s_variable"] = 5
        # elif nutrition["fru_s_prediction"] < fruit_serving_target-2 or nutrition["fru_s_prediction"] > fruit_serving_target+2:
        #     #print("fruits servings outside +-2")
        #     self.fru_s_counter += 1
        #     return None

        # Juice serving scoring
        juice_serving_target = 1
        nutrition["jui_s_variable"] = 0
        nutrition["jui_s_prediction"] = nutrition.get("jui_s", 0)
        if nutrition["jui_s_prediction"] > juice_serving_target:
            score *= 1
            nutrition["jui_s_variable"] = 1
        # elif nutrition["jui_s_prediction"] > 1:
        #     #print("juice servings over 1")
        #     self.jui_s_counter += 1
        #     return None

        # Plant protein quantity scoring
        leg_q_target = self.user_energy_intake*125/2500
        nutrition["plp_q_variable"] = 0
        nutrition["plp_q_prediction"] = nutrition.get("plp_q", 0)
        if nutrition["plp_q_prediction"] > leg_q_target*0.9:
            score += 10 * self.NUTRITION_WEIGHTS["plp_q"]
            nutrition["plp_q_variable"] = 10
        elif nutrition["plp_q_prediction"] > leg_q_target*0.8:
            score += 5 * self.NUTRITION_WEIGHTS["plp_q"]
            nutrition["plp_q_variable"] = 5
        elif nutrition["plp_q_prediction"] > leg_q_target*0.7:
            score += 0 * self.NUTRITION_WEIGHTS["plp_q"]
            nutrition["plp_q_variable"] = 0
        # elif nutrition["plp_q_prediction"] < leg_q_target*0.7:
        #     #print("legumes less than", leg_q_target*0.3)
        #     self.leg_q_counter += 1
        #     return None

        # Dairy quantity scoring
        dai_q_target = [self.user_energy_intake*125/2500, self.user_energy_intake*250/2500]
        nutrition["dai_q_variable"] = 0
        nutrition["dai_q_prediction"] = nutrition.get("dai_q", 0)
        if nutrition["dai_q_prediction"] >= self.user_energy_intake*125/2500 and nutrition["dai_q_prediction"] >= self.user_energy_intake*250/2500:
            score += 10 * self.NUTRITION_WEIGHTS["dai_q"]
            nutrition["dai_q_variable"] = 10
        elif nutrition["dai_q_prediction"] >= self.user_energy_intake*100/2500 and nutrition["dai_q_prediction"] >= self.user_energy_intake*275/2500:
            score += 0 * self.NUTRITION_WEIGHTS["dai_q"]
            nutrition["dai_q_variable"] = 0
        # elif nutrition["dai_q_prediction"] < self.user_energy_intake*100/2500 or nutrition["dai_q_prediction"] > self.user_energy_intake*275/2500:
        #     #print("dairy quantity outside", self.user_energy_intake*100/2500, self.user_energy_intake*275/2500)
        #     self.dai_q_counter += 1
        #     return None

        # Dairy serving scoring
        nutrition["dai_s_variable"] = 0
        nutrition["dai_s_prediction"] = nutrition.get("dai_s", 0)
        if 1 <= nutrition["dai_s_prediction"] <= 2:
            score += 10 * self.NUTRITION_WEIGHTS["dai_s"]
            nutrition["dai_s_variable"] = 10
        elif 0 <= nutrition["dai_s_prediction"] <= 3:
            score += 0 * self.NUTRITION_WEIGHTS["dai_s"]
            nutrition["dai_s_variable"] = 0
        # elif nutrition["dai_s_prediction"] > 3:
        #     #print("dairy servings more than 3")
        #     self.dai_s_counter += 1
        #     return None

        # Cheese quantity scoring
        cheese_quantity_ratget = self.user_energy_intake*25/2500
        nutrition["che_q_variable"] = 0
        nutrition["che_q_prediction"] = nutrition.get("che_q", 0)
        if nutrition["che_q_prediction"] >= cheese_quantity_ratget*0.95 and nutrition["che_q_prediction"] <= cheese_quantity_ratget*1.05:
            score += 10 * self.NUTRITION_WEIGHTS["che_q"]
            nutrition["che_q_variable"] = 10
        elif nutrition["che_q_prediction"] >= cheese_quantity_ratget*0.90 and nutrition["che_q_prediction"] <= cheese_quantity_ratget*1.1:
            score += 5 * self.NUTRITION_WEIGHTS["che_q"]
            nutrition["che_q_variable"] = 5
        elif nutrition["che_q_prediction"] >= cheese_quantity_ratget*0.85 and nutrition["che_q_prediction"] <= cheese_quantity_ratget*1.15:
            score += 0 * self.NUTRITION_WEIGHTS["che_q"]
            nutrition["che_q_variable"] = 0
        # elif nutrition["che_q_prediction"] < cheese_quantity_ratget*0.85 or nutrition["che_q_prediction"] > cheese_quantity_ratget*1.15:
        #     #print("cheese quantity outside +-15%")
        #     self.che_q_counter += 1
        #     return
        
        # Cheese serving scoring
        cheese_serving_ratget = 1
        nutrition["che_s_variable"] = 0
        nutrition["che_s_prediction"] = nutrition.get("che_s", 0)
        if nutrition["che_s_prediction"] == 1:
            score += 10 * self.NUTRITION_WEIGHTS["che_s"]
            nutrition["che_s_variable"] = 10
        elif 0 <= nutrition["che_s_prediction"] <= 2:
            score += 0 * self.NUTRITION_WEIGHTS["che_s"]
            nutrition["che_s_variable"] = 0
        # elif nutrition["che_s_prediction"] > 2:
        #     #print("cheese servings more than 2")
        #     self.che_s_counter += 1
        #     return

        # Nuts and seeds quantity scoring
        nuts_and_seeds_quantity_target = self.user_energy_intake*30/2500
        nutrition["nns_q_variable"] = 0
        nutrition["nns_q_prediction"] = nutrition.get("nns_q", 0)
        if nutrition["nns_q_prediction"] >= nuts_and_seeds_quantity_target*0.95 and  nutrition["nns_q_prediction"] <= nuts_and_seeds_quantity_target*1.05:
            score += 10 * self.NUTRITION_WEIGHTS["nns_q"]
            nutrition["nns_q_variable"] = 10
        elif nutrition["nns_q_prediction"] >= nuts_and_seeds_quantity_target*0.9 and  nutrition["nns_q_prediction"] <= nuts_and_seeds_quantity_target*1.1:
            score += 5 * self.NUTRITION_WEIGHTS["nns_q"]
            nutrition["nns_q_variable"] = 5
        elif nutrition["nns_q_prediction"] >= nuts_and_seeds_quantity_target*0.85 and  nutrition["nns_q_prediction"] <= nuts_and_seeds_quantity_target*1.15:
            score += 0 * self.NUTRITION_WEIGHTS["nns_q"]
            nutrition["nns_q_variable"] = 0
        # elif nutrition["nns_q_prediction"] < nuts_and_seeds_quantity_target*0.85 or  nutrition["nns_q_prediction"] > nuts_and_seeds_quantity_target*1.15:
        #     #print("nuts and seeds outside", nuts_and_seeds_quantity_target*0.85, nuts_and_seeds_quantity_target*1.15)
        #     self.nns_q_counter += 1
        #     return

        # Add meat to nutrition dictionary
        nutrition["mea_q_prediction"] = nutrition.get("mea_q", 0)
        nutrition["mea_s_prediction"] = nutrition.get("mea_s", 0)

        # Add fish to nutrition dictionary
        nutrition["fis_q_prediction"] = nutrition.get("fis_q", 0)
        nutrition["fis_s_prediction"] = nutrition.get("fis_s", 0)

        return score

    def process(self, meals):
        """Main processing pipeline"""

        total_combinations = len(meals[0])*len(meals[1])*len(meals[2])*len(meals[3])*len(meals[4])
        print("Total combinations:", total_combinations)
        if total_combinations > self.NUMBER_OF_SAMPLES:
            combinations = self._combinations("daily", 0, meals, self.NUMBER_OF_SAMPLES)
        else:
            combinations = self._combinations("daily", 0, meals, self.NUMBER_OF_SAMPLES)
        print("Final combinations:", len(combinations))
  
        top_plans = []
        temp_list = []
        print()
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

    def __init__(self, results):
        self.results = results
        self.meal_counts = defaultdict(int)  # Track meal occurrences in heap

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

    def _update_meal_counts(self, meal_ids: List[int], increment: bool):
        """NEW: Properly handle meal count updates"""
        delta = 1 if increment else -1
        for i, m in enumerate(meal_ids):
            if i in [5*x + offset for x in range(7) for offset in [0, 2, 4]]:  # Only track main meals
                self.meal_counts[m] += delta

    def process(self) -> List[Dict]:
        """Main processing pipeline"""
        top_plans = []
        combinations = self.generate_combinations()

        for idx, combo in enumerate(combinations):
            if idx == 100000:
                break
            
            meal_ids = [mid for np in combo for mid in np['meals']]
            #meal_ids = [m.id for m in combo]
            nutrition = self.calculate_nutrition(combo)
            score = self.score_meal_plan(nutrition)

            # Adjust score based on meal diversity
            if idx == 0:
                # print(meal_ids)
                # print(len(meal_ids))
                self._update_meal_counts(meal_ids, increment=True)
                # for m in self.meal_counts:
                #     print(m, self.meal_counts[m])
                # quit()
            penalty = sum(self.meal_counts[mid] for np in combo for mid in np['meals']) * 0.1  # Small penalty for repetition
            score -= penalty  # Reduce score if meals repeat
            
            entry = (score, idx, {
                "meals": [m['meals'] for m in combo],
                "score": score,
                "nutrition": nutrition,
            })

            if all(self.meal_counts[m] < 3 for m in meal_ids):
                if len(top_plans) <= TOP_PLANS:
                    heapq.heappush(top_plans, entry)
                    self._update_meal_counts(meal_ids, increment=True)
                else:
                    if score > top_plans[0][0]:
                        removed = heapq.heappop(top_plans)
                        self._update_meal_counts(removed[2]["meals"], increment=False)
                        heapq.heappush(top_plans, entry)
                        self._update_meal_counts(meal_ids, increment=True)

            # heapq.heappush(top_plans, entry)
            
            # if len(top_plans) > 2:
            #     heapq.heappop(top_plans)

        for m in self.meal_counts:
            print(m, self.meal_counts[m])
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
        print("energy", daily_generator.energy_target, daily_generator.energy_counter)
        print("protein", daily_generator.protein_target, daily_generator.protein_counter)
        print("carbs", daily_generator.carbs_target, daily_generator.carbs_counter)
        print("fats", daily_generator.fats_target, daily_generator.fats_counter)
        print("fibre", daily_generator.fibre_target, daily_generator.fibre_counter)
        print("calcium", daily_generator.calcium, daily_generator.calcium_counter)
        print("iron", daily_generator.iron, daily_generator.iron_counter)
        print("folate", daily_generator.folate, daily_generator.folate_counter)
        print("veg_q", daily_generator.veg_q_target, daily_generator.veg_q_counter)
        print("veg_s", daily_generator.veg_s_target, daily_generator.veg_s_counter)
        print("fru_q", daily_generator.fru_q_target, daily_generator.fru_q_counter)
        print("fru_s", daily_generator.fru_s_target, daily_generator.fru_s_counter)
        print("jui_s", daily_generator.jui_s_target, daily_generator.jui_s_counter)
        print("leg_q", daily_generator.leg_q_target, daily_generator.leg_q_counter)
        print("dai_q", daily_generator.dai_q_target, daily_generator.dai_q_counter)
        print("dai_s", daily_generator.dai_s_target, daily_generator.dai_s_counter)
        print("che_q", daily_generator.che_q_target, daily_generator.che_q_counter)
        print("che_s", daily_generator.che_s_target, daily_generator.che_s_counter)
        print("nns_q", daily_generator.nns_q_target, daily_generator.nns_q_counter)
        self.daily_dataframe_transform(daily_results)

        #weekly_generator = WeeklyMealPlanGenerator(daily_results)
        #weekly_results = weekly_generator.process()
        #self.weekly_dataframe_transform(weekly_results)
        #self.print_best_week(weekly_results[0])

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
            