from django.core.management.base import BaseCommand
import numpy as np
import time
import pandas as pd
import math
import matplotlib.pyplot as plt
from scipy.stats import norm
import scipy.stats as stats
import itertools
from app.management.commands.np_generator_v4 import return_best_plan
import time
from datetime import timedelta
import datetime
import csv
import os
import seaborn as sns

use_cases = [
    ["none", "omnivore", 403], ["none", "pescatarian", 14], ["none", "vegetarian", 32], ["none", "vegan", 9],
    ["milk_allergy", "omnivore", 24], ["milk_allergy", "pescatarian", 1], ["milk_allergy", "vegetarian", 2], ["milk_allergy", "vegan", 0],
    ["nuts_allergy", "omnivore", 11], ["nuts_allergy", "pescatarian", 0], ["nuts_allergy", "vegetarian", 1], ["nuts_allergy", "vegan", 0],
    ["milk_nuts_allergy", "omnivore", 6], ["milk_nuts_allergy", "pescatarian", 0], ["milk_nuts_allergy", "vegetarian", 0], ["milk_nuts_allergy", "vegan", 0],
]

# use_cases = [
#     ["none", "omnivore", 1], ["none", "pescatarian", 1], ["none", "vegetarian", 1], ["none", "vegan", 1],
#     ["milk_allergy", "omnivore", 1], ["milk_allergy", "pescatarian", 1], ["milk_allergy", "vegetarian", 1], ["milk_allergy", "vegan", 1],
#     ["nuts_allergy", "omnivore", 1], ["nuts_allergy", "pescatarian", 1], ["nuts_allergy", "vegetarian", 1], ["nuts_allergy", "vegan", 1],
#     ["milk_nuts_allergy", "omnivore", 1], ["milk_nuts_allergy", "pescatarian", 1], ["milk_nuts_allergy", "vegetarian", 1], ["milk_nuts_allergy", "vegan", 1],
# ]

def generate_single_user(args):
    aa, kcal, sex, preference, allergy, country = args

    user_profile = {
        'a/a': aa,
        'energy_intake': kcal,
        'base_energy': 2500,
        'preference': preference,
        'allergy': allergy,
        'cuisine': country,
        'sex': sex,
    }

    plan, status_code = return_best_plan(user_profile)
    if plan is None:
        plan = create_nan_plan(aa, status_code)
    return plan

def create_nan_plan(aa, status_code):
    plan = {
        'a/a': aa,
        'dd': status_code,
        'DNPS': np.nan,
        'NDNPS': np.nan,
    }

    for day in range(1, 8):
        for nutrient in [
            'Total_Energy', 'Total_Protein', 'Total_Fat', 'Total_Carbs', 'Total_Fibre',
            'Total_Calcium', 'Total_Iron', 'Total_Folate',
            'veg_q', 'veg_s', 'fru_q', 'fru_s', 'jui_s', 'leg_q',
            'dai_q', 'dai_s', 'che_q', 'che_s', 'nns_q', 'mea_q', 'mea_s',
            'blv_q', 'blv_s', 'fis_q', 'fis_s', 'oif_q', 'oif_s'
        ]:
            plan[f'day_{day}_{nutrient}'] = np.nan
            plan[f'day_{day}_{nutrient}_target'] = np.nan

    for nutrient in [
        'Total_Energy', 'Total_Protein', 'Total_Fat', 'Total_Carbs', 'Total_Fibre',
        'Total_Calcium', 'Total_Iron', 'Total_Folate',
        'veg_q', 'veg_s', 'fru_q', 'fru_s', 'jui_s', 'leg_q',
        'dai_q', 'dai_s', 'che_q', 'che_s', 'nns_q', 'mea_q', 'mea_s',
        'blv_q', 'blv_s', 'fis_q', 'fis_s', 'oif_q', 'oif_s'
    ]:
        plan[f'week_{nutrient}'] = np.nan
        plan[f'week_{nutrient}_target'] = np.nan

    return plan

class Command(BaseCommand):
    help = 'Generate user profiles'

    def handle(self, *args, **kwargs):
        total_users = sum(n_samples for allergy, preference, n_samples in use_cases) * 4 * 2
        check_point_counter = 0

        start_global = time.time()

        # Code to iterate through each country, allergy, preference, sex, kcal and retrieve the best weekly meal plan.
        counter = 1
        #for country in [["Irish"], ["Spain"], ["Hungary"], ["Irish", "Spain"], ["Irish", "Hungary"], ["Spain", "Hungary"], ["Irish", "Spain", "Hungary"]]:
        for country in [["Irish"], ["Spain"], ["Hungary"], ["Irish", "Spain", "Hungary"]]:
            results = []
            aa = 1
            for allergy, preference, n_samples in use_cases:
                for sex in ['male', 'female']:
                    calories = self.normal_dis(sex, n_samples)
                    #self.plot_normal_distribution(calories, '_'.join(country), sex, n_samples)
                    for _, kcal in enumerate(calories):
                        args_list = [aa, kcal, sex, preference, allergy, country]

                        results.append(generate_single_user(args_list))

                        elapsed_global = time.time() - start_global
                        avg_time_per_user = elapsed_global / counter
                        remaining_users = total_users - counter
                        eta_seconds = remaining_users * avg_time_per_user
                        eta_formatted = str(timedelta(seconds=int(eta_seconds)))
                        print(f"{'_'.join(country)}, {aa}, {kcal} | User {counter}/{total_users} | ETA: {eta_formatted}", flush=True)
                        counter += 1
                        aa += 1

            df = pd.DataFrame(results)
            filename = f"{'_'.join(country)}.csv"
            df.to_csv(f'/home/tsolakidis/Desktop/planeat/recommender_v1/virtual_users/{filename}', index=False)

    def normal_dis(self, sex, n_samples):
        # Set the mean and standard deviation for calories
        mean = 2500 if sex == 'male' else 2000
        std = 1000/3 if sex == 'male' else 4000/15

        # Generate random calories for each user
        calories = np.random.normal(loc=mean, scale=std, size=n_samples)

        return calories

    def plot_normal_distribution(self, calories, country, sex, n_samples):
        plt.figure(figsize=(10, 6))
        sns.histplot(calories, kde=True, bins=30, color='skyblue')
        plt.title(f'Normal Distribution of Calories: {sex.capitalize()}, {country}, {n_samples} users')
        plt.xlabel('Calories')
        plt.ylabel('Frequency')
        plt.grid(True)

        # Create output folder if it doesn't exist
        #output_dir = "/home/tsolakidis/Desktop/planeat/recommender_v1/virtual_users/"

        # Save the figure
        filename = f"dis_{country}_{sex}_{n_samples}.png".replace(" ", "")
        plt.savefig(f'/home/tsolakidis/Desktop/planeat/recommender_v1/virtual_users/dis_{country}_{sex}_{n_samples}.png')
        plt.close()
