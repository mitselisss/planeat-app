from django.core.management.base import BaseCommand
from app.models import Meal
import pandas as pd
from django.db import transaction
from django.db.models import Q
import random
import itertools
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import json
import os
import math
import matplotlib.pyplot as plt

fields = [
    'Total_Energy',
    'Total_Protein', 'Total_Fat',
    'Total_Carbs',
    'Total_Fibre',
    'Total_Calcium', 'Total_Iron', 'Total_Folate',
    'veg_q',
    #'veg_s',
    'fru_q',
    #'fru_s',
    #'jui_s',
    'leg_q',
    'dai_q',
    #'dai_s',
    'che_q',
    #'che_s',
    'nns_q',
    'mea_q',
    #'mea_s',
    'blv_q',
    #'blv_s',
    'fis_q',
    #'fis_s',
    'oif_q',
    #'oif_s',
]

class Command(BaseCommand):
    help = 'Import data from dish CSV files into Dish model'
    def handle(self, *args, **kwargs):
        self.stdout.write('Starting databases analyzation...')
        with transaction.atomic():
            #self.create_csvs()
            #self.plot()
            self.get_statistics()
        self.stdout.write(self.style.SUCCESS('Databases analyzation complete.'))

    def _filtering(self, cuisine, user_preference, user_allergy, season):
        '''
        Function that filters the whole meals' database based on:
        seasonality, user's preferences, user's allergies, and
        cuisine county/countries
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
        """Functions that returns the five meals"""
        meals = [
            meals.filter(Type="Breakfast"),
            meals.filter(Type="Snack"),
            meals.filter(Type="Lunch"),
            meals.filter(Type="Snack"),
            meals.filter(Type="Dinner")
        ]
        return meals

    def _random_combination_generator(self, meal_groups):
        """Memory-efficient random sampling without pre-generation"""
        for _ in range(100000):
            yield tuple(
                random.choice(group)
                for group in meal_groups
            )

    def calculate_nutrition(self, combo):
        nutrition_totals = {}
        for field in fields:
            nutrition_totals[field] = sum(getattr(c, field) for c in combo)
        return nutrition_totals

    def create_csvs(self):
        '''Create and save csv files for each cuisine, season, preference, and allergy'''
        counter = 0
        for cuisine in [["Irish"], ["Spain"], ["Hungary"], ["Irish", "Spain"], ["Irish", "Hungary"], ["Spain", "Hungary"], ["Irish", "Spain", "Hungary"]]:
            for season in ["summer", "autumn", "winter", "spring"]:
                for user_preference in ["omnivore", "pescatarian", "vegetarian", "vegan"]:
                    for user_allergy in ["none", "milk_allergy", "nuts_allergy"]:
                        meals = self._filtering(cuisine, user_preference, user_allergy, season)
                        if len(meals) == 0:
                            print("error in _filtering")
                            quit()
                        meals = self._get_five_meals(meals)
                        if len(meals) == 0:
                            print("error in _get_five_meals")
                            quit()

                        total = []
                        for idx, combo in enumerate(self._random_combination_generator(meals)):
                            nutrition = self.calculate_nutrition(combo)
                            total.append(nutrition)
                        df = pd.DataFrame(total)
                        df.to_csv(f'../db_analyzation/{results}_{season}_{user_preference}_{user_allergy}.csv', index=False)
                        counter += 1
                        results = '_'.join(cuisine)
                        print(f'{results}_{season}_{user_preference}_{user_allergy}_{counter}.csv/{7*4*4*3}')

    def plot_hist(self, path, df):
        '''Create and save png for histograms for each cuisine, season, preference, and allergy'''
        num_fields = len(fields)
        cols = 5  # number of columns in subplot grid
        rows = math.ceil(num_fields / cols)

        fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3))
        axes = axes.flatten()

        for i, col in enumerate(fields):
            data = df[col].dropna()  # drop NaNs to avoid issues
            mean = data.mean()
            std = data.std()

            # Plot histogram
            data.plot(kind='hist', ax=axes[i], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
            axes[i].set_title(col)

            # Add mean and std text in top-right corner
            axes[i].text(0.95, 0.95,
                        f"μ = {mean:.2f}\nσ = {std:.2f}",
                        verticalalignment='top',
                        horizontalalignment='right',
                        transform=axes[i].transAxes,
                        fontsize=8,
                        bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.3'))

        # Remove unused axes
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        plt.savefig(f'{path+"_hist.png"}')
        plt.close()
        print(f'{path}.hist')

    def plot_heap_map(self, path, df):
        '''Create and save png for heat maps for each cuisine, season, preference, and allergy'''
        plt.figure(figsize=(12, 10))
        sns.heatmap(df.corr(), annot=True, fmt=".2f", cmap='coolwarm', square=True)

        plt.title("Correlation Matrix")
        plt.tight_layout()
        plt.savefig(path+"_corr.png", dpi=300)  # Save as PNG
        plt.close()
        print(f'{path}.corr')

    def plot(self):
        '''Read all csv files and plot histograms and heat maps'''
        folder = "/home/tsolakidis/Desktop/planeat/recommender_v1/db_analyzation"
        dir_list = os.listdir(folder)
        for csv in dir_list:
            if csv.endswith(".csv"):
                df = pd.read_csv(folder+"/"+csv)
                self.plot_hist(folder+"/"+csv.split(".")[0], df)
                self.plot_heap_map(folder+"/"+csv.split(".")[0], df)

    def get_statistics(self):
        '''Get min, max, mean, and std of every item for each cuisine'''

        country = {}
        # Short names for dict keys, strip 'Total_' and lowercase
        short_names = [f.replace('Total_', '').lower() for f in fields]

        for combo in [["Ireland"], ["Spain"], ["Hungary"], ["Ireland", "Spain", "Hungary"]]:
            # Load nutrient arrays per meal type
            groups = []
            for meal_type in ['Breakfast', 'Snack', 'Lunch', 'Snack', 'Dinner']:
                qs = Meal.objects.filter(Country__in=combo, Type=meal_type)
                data = np.array(list(qs.values_list(*fields)), dtype=float)
                if data.size == 0:
                    self.stdout.write(f"Skipping {combo}: no data for {meal_type}")
                    break
                groups.append(data)

            else:
                # Compute per-group stats (min, max, mean, var)
                mins  = np.stack([g.min(axis=0)  for g in groups])
                maxs  = np.stack([g.max(axis=0)  for g in groups])
                means = np.stack([g.mean(axis=0) for g in groups])
                vars_ = np.stack([g.var(axis=0, ddof=0) for g in groups])

                # Aggregate across meal types
                sum_min  = mins.sum(axis=0)
                sum_max  = maxs.sum(axis=0)
                sum_mean = means.sum(axis=0)
                sum_std  = np.sqrt(vars_.sum(axis=0))

                # Build dict for this country combo
                key = '_'.join(combo) + '_'
                stats = {}
                for i, name in enumerate(short_names):
                    stats[f"{name}_min"]  = float(sum_min[i])
                    stats[f"{name}_max"]  = float(sum_max[i])
                    stats[f"{name}_mea"]  = float(sum_mean[i])
                    stats[f"{name}_std"]  = float(sum_std[i])

                country[key] = stats

        # Now self.country holds structured results
        # Optionally, print or save as needed
        for combo_key, stats in country.items():
            self.stdout.write(f"{combo_key}: {stats}\n")
