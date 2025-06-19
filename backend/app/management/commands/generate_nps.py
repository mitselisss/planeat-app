from django.core.management.base import BaseCommand
from app.models import Meal
import pandas as pd
from django.db import transaction
from django.db.models import Q
import random
import itertools
from itertools import combinations
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import json
import time

user_energy_intake = 2500
user_weight = 80

daily_targets = {
    "Total_Energy": user_energy_intake,

    "Total_Protein": 0.83*user_weight,
    "Total_Fat": 0.325*user_energy_intake/9,
    "Total_Carbs": 0.575*user_energy_intake/4,
    "Total_Fibres": 22.5,

    "Total_Calcium": 1000,
    "Total_Iron": 17,
    "Total_Folate": 330,

    "prm_q": 0,
    "prm_s": 0,
    "mea_q": 0,
    "mea_s": 0,
    "veg_q": 300,
    "veg_s": 3,
    "fru_q": 200,
    "fru_s": 2,
    "jui_q": 0,
    "jui_s": 1,
    "dai_q": 187.5,
    "dai_s": 2,
    "che_q": 25,
    "che_s": 1,
    "leg_q": 125,
    "leg_s": 0,
    "nns_q": 30,
    "nns_s": 0,
    "fis_q": 0,
    "fis_s": 0,
    "oif_q": 0,
    "oif_s": 0,
}

weekly_targets = {
    "Total_Energy": user_energy_intake*7,

    "Total_Protein": 0.83*user_weight*7,
    "Total_Fat": 0.325*user_energy_intake/9*7,
    "Total_Carbs": 0.575*user_energy_intake/4*7,
    "Total_Fibres": 22.5*7,

    "Total_Calcium": 1000*7,
    "Total_Iron": 17*7,
    "Total_Folate": 330*7,

    "prm_q": 0,
    "prm_s": 0,
    "mea_q": 420,
    "mea_s": 3,
    "veg_q": 300*7,
    "veg_s": 3*7,
    "fru_q": 200*7,
    "fru_s": 2*7,
    "jui_q": 0,
    "jui_s": 1*7,
    "dai_q": 187.5*7,
    "dai_s": 2*7,
    "che_q": 25*7,
    "che_s": 1*7,
    "leg_q": 125*7,
    "leg_s": 0,
    "nns_q": 30*7,
    "nns_s": 0,
    "fis_q": 200,
    "fis_s": 2,
    "oif_q": 100,
    "oif_s": 1,
}

class Command(BaseCommand):
    help = 'Import data from dish CSV files into Dish model'
    def handle(self, *args, **kwargs):
        self.stdout.write('Starting generation of daily nps...')
        with transaction.atomic():
            self.generator()
        self.stdout.write(self.style.SUCCESS('Generation of daily nps complete.'))

    def _filtering(self, cuisine, user_preference, user_allergy, season):
        '''
        Function that filters the whole meals' database based on
        seasonality, user's preferences, user's allergies, and
        cuisine county/countries and retrieves the meals that are
        fulfill these prerecuisites.
        '''

        SEASON_FILTERS = {
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
            SEASON_FILTERS[season] &
            Q(Country__in=cuisine) &
            PREFERENCE_FILTERS.get(user_preference, Q()) &  # Default to empty Q if preference not found
            ALLERGY_FILTERS.get(user_allergy, Q())  # Default to empty Q if allergy not found
        )

        return Meal.objects.filter(query)

    def _get_five_meals(self, meals):
        """Function that returns lists of meals grouped by type."""
        return [
            list(meals.filter(Type="Breakfast")),   # Convert QuerySet to list
            list(meals.filter(Type="Snack")),       # Morning Snack
            list(meals.filter(Type="Lunch")),      
            list(meals.filter(Type="Snack")),       # Afternoon Snack
            list(meals.filter(Type="Dinner"))
        ]

    def _generate_sample_meal_plans(self, meals, top_n=20):
        """Generates sample meal plans with scores and sorts by best match."""
        breakfasts, snacks1, lunches, snacks2, dinners = meals
        
        sample_size = len(breakfasts)*len(snacks1)*len(lunches)*len(snacks2)*len(dinners)
        sample_size = 100000

        start_time = time.time()
        meal_combinations_processed = 0

        meal_plans = []

        combos = itertools.product(breakfasts, snacks1, lunches, snacks2, dinners)
        
        print("\nGenerating sample meal plans with scores...\n")
        #for idx, combo in enumerate(combos):
        for _ in range(sample_size):
            # if idx == 100000:
            #     break
            # # Compute total nutrition values
            # meal_plan = {
            #     "Breakfast": combo[0].id,
            #     "Morning Snack": combo[1].id,
            #     "Lunch": combo[2].id,
            #     "Afternoon Snack": combo[3].id,
            #     "Dinner": combo[4].id,
            #     "Total Energy (kcal)": sum(m.Total_Energy for m in combo),
            #     "Total Protein (g)": sum(m.Total_Protein for m in combo),
            #     "Total Fat (g)": sum(m.Total_Fat for m in combo),
            #     "Total Carbs (g)": sum(m.Total_Carbs for m in combo)
            # }

            # Select random meals
            breakfast = random.choice(breakfasts)
            morning_snack = random.choice(snacks1)
            lunch = random.choice(lunches)
            afternoon_snack = random.choice(snacks2)
            dinner = random.choice(dinners)

            # Compute total nutrition values
            meal_plan = {
                "Total_Energy": sum(m.Total_Energy for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),

                "Total_Protein": sum(m.Total_Protein for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "Total_Fat": sum(m.Total_Fat for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "Total_Carbs": sum(m.Total_Carbs for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "Total_Fibres": sum(m.Total_Fibre for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),

                "Total_Calcium": sum(m.Total_Calcium for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "Total_Iron": sum(m.Total_Iron for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "Total_Folate": sum(m.Total_Folate for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),

                "prm_q": sum(m.prm_q for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "prm_s": sum(m.prm_s for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "mea_q": sum(m.mea_q for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "mea_s": sum(m.mea_s for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "veg_q": sum(m.veg_q for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "veg_s": sum(m.veg_s for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "fru_q": sum(m.fru_q for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "fru_s": sum(m.fru_s for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "jui_q": sum(m.jui_q for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "jui_s": sum(m.jui_s for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "dai_q": sum(m.dai_q for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "dai_s": sum(m.dai_s for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "che_q": sum(m.che_q for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "che_s": sum(m.che_s for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "leg_q": sum(m.leg_q for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "leg_s": sum(m.leg_s for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "nns_q": sum(m.nns_q for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "nns_s": sum(m.nns_s for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "fis_q": sum(m.fis_q for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "fis_s": sum(m.fis_s for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "oif_q": sum(m.oif_q for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),
                "oif_s": sum(m.oif_s for m in [breakfast, morning_snack, lunch, afternoon_snack, dinner]),

                "Breakfast": breakfast.id,
                "Morning Snack": morning_snack.id,
                "Lunch": lunch.id,
                "Afternoon Snack": afternoon_snack.id,
                "Dinner": dinner.id,                
            }

            # Score the meal plan
            meal_plan["Score"] = self._score_meal_plan(meal_plan)

            meal_plans.append(meal_plan)

            meal_combinations_processed += 1
            # For performance, we are not storing results but just processing
            if meal_combinations_processed % 100000 == 0:  # Print every 100k combinations
                print(f"Processed {meal_combinations_processed} meal combinations...")

        # Sort meal plans by score (highest score first)
        sorted_meal_plans = sorted(meal_plans, key=lambda x: x["Score"], reverse=True)

        # Get the top N meal plans
        top_meal_plans = sorted_meal_plans[:top_n]

        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        print(f"Processed {meal_combinations_processed} meal combinations in {elapsed_time:.2f} seconds.")

        return top_meal_plans

    def _score_meal_plan(self, meal_plan):
        """Scores a meal plan based on how well it meets nutritional targets."""
        
        # Define target daily intake (can later be user-customizable)
        TARGETS = {
            "Total_Energy": user_energy_intake,

            "Total_Protein": 0.83*user_weight,
            "Total_Fat": 0.325*user_energy_intake/9,
            "Total_Carbs": 0.575*user_energy_intake/4,
            "Total_Fibres": 22.5,

            "Total_Calcium": 1000,
            "Total_Iron": 17,
            "Total_Folate": 330,

            "prm_q": 0,
            "prm_s": 0,
            "mea_q": 0,
            "mea_s": 0,
            "veg_q": 300,
            "veg_s": 3,
            "fru_q": 200,
            "fru_s": 2,
            "jui_q": 0,
            "jui_s": 1,
            "dai_q": 187.5,
            "dai_s": 2,
            "che_q": 25,
            "che_s": 1,
            "leg_q": 125,
            "leg_s": 0,
            "nns_q": 30,
            "nns_s": 0,
            "fis_q": 0,
            "fis_s": 0,
            "oif_q": 0,
            "oif_s": 0,
        }
        
        # Calculate score (lower deviation from target = better)
        score = 0
        for key, target in TARGETS.items():
            actual = meal_plan[key]
            score -= abs(actual - target)  # Penalize deviations

        return score

    def _score_weekly_meal_plan(self, weekly_meal_plan):
        """Scores a meal plan based on how well it meets nutritional targets."""
        
        # Define target daily intake (can later be user-customizable)
        TARGETS = {
            "Total_Energy": user_energy_intake*7,

            "Total_Protein": 0.83*user_weight*7,
            "Total_Fat": 0.325*user_energy_intake/9*7,
            "Total_Carbs": 0.575*user_energy_intake/4*7,
            "Total_Fibres": 22.5*7,

            "Total_Calcium": 1000*7,
            "Total_Iron": 17*7,
            "Total_Folate": 330*7,

            "prm_q": 0,
            "prm_s": 0,
            "mea_q": 420,
            "mea_s": 3,
            "veg_q": 300*7,
            "veg_s": 3*7,
            "fru_q": 200*7,
            "fru_s": 2*7,
            "jui_q": 0,
            "jui_s": 1*7,
            "dai_q": 187.5*7,
            "dai_s": 2*7,
            "che_q": 25*7,
            "che_s": 1*7,
            "leg_q": 125*7,
            "leg_s": 0,
            "nns_q": 30*7,
            "nns_s": 0,
            "fis_q": 200,
            "fis_s": 2,
            "oif_q": 100,
            "oif_s": 1,
        }
        
        # Calculate score (lower deviation from target = better)
        score = 0
        for key, target in TARGETS.items():
            actual = weekly_meal_plan[key]
            score -= abs(actual - target)  # Penalize deviations

        return score

    def _generate_weekly_plan(self, top_meal_plans, top_n=20):
        combos = combinations(top_meal_plans, 7)
        weekly_meal_plans = []

        start_time = time.time()
        meal_combinations_processed = 0

        print("\nGenerating sample meal plans with scores...\n")
        for combo in combos:
            # for m in combo:
            #     print(m["Breakfast"])
            # quit()
            # Compute total weekly nutrition values
            weekly_meal_plan = {
                "Total_Energy": sum(m["Total_Energy"] for m in combo),

                "Total_Protein": sum(m["Total_Protein"] for m in combo),
                "Total_Fat": sum(m["Total_Fat"] for m in combo),
                "Total_Carbs": sum(m["Total_Carbs"] for m in combo),
                "Total_Fibres": sum(m["Total_Fibres"] for m in combo),

                "Total_Calcium": sum(m["Total_Calcium"] for m in combo),
                "Total_Iron": sum(m["Total_Iron"] for m in combo),
                "Total_Folate": sum(m["Total_Folate"] for m in combo),

                "prm_q": sum(m["prm_q"] for m in combo),
                "prm_s": sum(m["prm_s"] for m in combo),
                "mea_q": sum(m["mea_q"] for m in combo),
                "mea_s": sum(m["mea_s"] for m in combo),
                "veg_q": sum(m["veg_q"] for m in combo),
                "veg_s": sum(m["veg_s"] for m in combo),
                "fru_q": sum(m["fru_q"] for m in combo),
                "fru_s": sum(m["fru_s"] for m in combo),
                "jui_q": sum(m["jui_q"] for m in combo),
                "jui_s": sum(m["jui_s"] for m in combo),
                "dai_q": sum(m["dai_q"] for m in combo),
                "dai_s": sum(m["dai_s"] for m in combo),
                "che_q": sum(m["che_q"] for m in combo),
                "che_s": sum(m["che_s"] for m in combo),
                "leg_q": sum(m["leg_q"] for m in combo),
                "leg_s": sum(m["leg_s"] for m in combo),
                "nns_q": sum(m["nns_q"] for m in combo),
                "nns_s": sum(m["nns_s"] for m in combo),
                "fis_q": sum(m["fis_q"] for m in combo),
                "fis_s": sum(m["fis_s"] for m in combo),
                "oif_q": sum(m["oif_q"] for m in combo),
                "oif_s": sum(m["oif_s"] for m in combo),
                
                "meal_ids": list((m["Breakfast"], m["Morning Snack"], m["Lunch"], m["Afternoon Snack"], m["Dinner"]) for m in combo),
            }

            # Score the meal plan
            weekly_meal_plan["Score"] = self._score_weekly_meal_plan(weekly_meal_plan)

            weekly_meal_plans.append(weekly_meal_plan)

            meal_combinations_processed += 1
            # For performance, we are not storing results but just processing
            if meal_combinations_processed % 100000 == 0:  # Print every 100k combinations
                print(f"Processed {meal_combinations_processed} weekly combinations...")

        # Sort meal plans by score (highest score first)
        sorted_weekly_meal_plans = sorted(weekly_meal_plans, key=lambda x: x["Score"], reverse=True)

        # Get the top N meal plans
        top_weekly_meal_plans = sorted_weekly_meal_plans[:top_n]

        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        print(f"Processed {meal_combinations_processed} meal combinations in {elapsed_time:.2f} seconds.")

        return top_weekly_meal_plans

    def _std(self, predicted, target):
        if target != 0:
            return abs(predicted-target)/target
        else:
            return 0
    
    def _print_daily_plans(self, top_daily_meal_plans):
        data = []
        for daily_plan in top_daily_meal_plans:
            temp = {}
            for key, predicted in daily_plan.items():
                if key in ["Breakfast", "Morning Snack", "Lunch", "Afternoon Snack", "Dinner", "Score"]:
                    continue
                temp[key] = self._std(predicted, daily_targets[key])
            data.append(temp)

        # Convert to DataFrame
        df = pd.DataFrame(list(daily_targets))
        print(df)
        df = pd.DataFrame(top_daily_meal_plans)
        print(df)
        df = pd.DataFrame(data)
        print(df)

    def _print_weekly_plans(self, top_weekly_meal_plans):
        data = []
        for weekly_plan in top_weekly_meal_plans:
            temp = {}
            for key, predicted in weekly_plan.items():
                if key in ["meal_ids", "Score"]:
                    continue
                temp[key] = self._std(predicted, weekly_targets[key])
            data.append(temp)

        # Convert to DataFrame
        df = pd.DataFrame([weekly_targets])
        print(df)
        df = pd.DataFrame(top_weekly_meal_plans)
        print(df)
        df = pd.DataFrame(data)
        print(df)

    def generator(self):
        cuisine = ["Irish"]
        user_preference = "omnivore"
        user_allergy = "none"
        season = "spring"

        meals = self._filtering(cuisine, user_preference, user_allergy, season)
        print("Number of meals after filtering:", len(meals))
        meals = self._get_five_meals(meals)
        print("Breakfasts:", len(meals[0]))
        print("Morning Snacks:", len(meals[1]))
        print("Lunches:", len(meals[2]))
        print("Afternoon Snack:", len(meals[3]))
        print("Dinners:", len(meals[4]))
        print("Total combinations:", len(meals[0])*len(meals[1])*len(meals[2])*len(meals[3])*len(meals[4]))

        # Generate sample meal plans
        top_daily_meal_plans = self._generate_sample_meal_plans(meals)
        top_weekly_meal_plans = self._generate_weekly_plan(top_daily_meal_plans)

        self._print_daily_plans(top_daily_meal_plans)
        self._print_weekly_plans(top_weekly_meal_plans)