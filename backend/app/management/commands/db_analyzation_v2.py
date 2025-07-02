from django.core.management.base import BaseCommand
from app.models import Meal
from itertools import product
import matplotlib.pyplot as plt
import numpy as np
import statistics

class Command(BaseCommand):
    help = 'Analyze the three databases.'

    def handle(self, *args, **kwargs):
        countries = [["Ireland"], ["Spain"], ["Hungary"]]

        num_samples = 10000000  # or make it configurable

        for country in countries:
            self.stdout.write(f'\nSampling for {country}...')

            # Load only Total_Energy values from DB
            breakfasts = list(Meal.objects.filter(Country__in=country, Type='Breakfast').values_list('Total_Energy', flat=True))
            snacks = list(Meal.objects.filter(Country__in=country, Type='Snack').values_list('Total_Energy', flat=True))
            lunches = list(Meal.objects.filter(Country__in=country, Type='Lunch').values_list('Total_Energy', flat=True))
            dinners = list(Meal.objects.filter(Country__in=country, Type='Dinner').values_list('Total_Energy', flat=True))

            if not all([breakfasts, snacks, lunches, dinners]):
                self.stdout.write(self.style.WARNING(f"Not enough data for {country}, skipping."))
                continue

            # Sample with replacement using numpy
            kcal_b = np.random.choice(breakfasts, size=num_samples, replace=True)
            kcal_msnack = np.random.choice(snacks, size=num_samples, replace=True)
            kcal_l = np.random.choice(lunches, size=num_samples, replace=True)
            kcal_asnack = np.random.choice(snacks, size=num_samples, replace=True)
            kcal_d = np.random.choice(dinners, size=num_samples, replace=True)

            # Sum daily totals
            total_kcals = kcal_b + kcal_msnack + kcal_l + kcal_asnack + kcal_d

            # Compute stats
            mean = np.mean(total_kcals)
            median = np.median(total_kcals)
            std = np.std(total_kcals)

            self.stdout.write(self.style.SUCCESS(
                f"{country[0]} Stats — Mean: {mean:.2f}, Median: {median:.2f}, Std: {std:.2f}"
            ))

            # Plot histogram
            plt.figure()
            plt.hist(total_kcals, bins=50)
            plt.title(f'{country[0]} - Total Daily Kcal Distribution')
            plt.xlabel('Total kcal')
            plt.ylabel('Frequency')
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f'{country[0].lower()}_daily_kcal_histogram.png')
            self.stdout.write(f"Saved histogram as {country[0].lower()}_daily_kcal_histogram.png")