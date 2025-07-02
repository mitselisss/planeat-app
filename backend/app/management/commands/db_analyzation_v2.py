from django.core.management.base import BaseCommand
from app.models import Meal
import matplotlib.pyplot as plt
import numpy as np

class Command(BaseCommand):
    help = 'Efficiently analyze meals by country and in total.'

    def sample_and_analyze(self, label, country, num_samples):
        # Fetch kcal arrays for each type
        if country:
            breakfasts = np.array(
                Meal.objects.filter(Country__in=country, Type='Breakfast').values_list('Total_Energy', flat=True), dtype=np.float32)
            snacks = np.array(
                Meal.objects.filter(Country__in=country, Type='Snack').values_list('Total_Energy', flat=True), dtype=np.float32)
            lunches = np.array(
                Meal.objects.filter(Country__in=country, Type='Lunch').values_list('Total_Energy', flat=True), dtype=np.float32)
            dinners = np.array(
                Meal.objects.filter(Country__in=country, Type='Dinner').values_list('Total_Energy', flat=True), dtype=np.float32)
        else:
            breakfasts = np.array(
                Meal.objects.filter(Type='Breakfast').values_list('Total_Energy', flat=True), dtype=np.float32)
            snacks = np.array(
                Meal.objects.filter(Type='Snack').values_list('Total_Energy', flat=True), dtype=np.float32)
            lunches = np.array(
                Meal.objects.filter(Type='Lunch').values_list('Total_Energy', flat=True), dtype=np.float32)
            dinners = np.array(
                Meal.objects.filter(Type='Dinner').values_list('Total_Energy', flat=True), dtype=np.float32)

        if not all([len(breakfasts), len(snacks), len(lunches), len(dinners)]):
            self.stdout.write(self.style.WARNING(f"Not enough data for {label}, skipping."))
            return

        # Sample with replacement
        kcal_b = np.random.choice(breakfasts, size=num_samples, replace=True)
        kcal_snacks = np.random.choice(snacks, size=(2, num_samples), replace=True)
        kcal_l = np.random.choice(lunches, size=num_samples, replace=True)
        kcal_d = np.random.choice(dinners, size=num_samples, replace=True)

        # Sum total kcals
        total_kcals = kcal_b + kcal_snacks.sum(axis=0) + kcal_l + kcal_d

        # Stats
        mean = np.mean(total_kcals)
        median = np.median(total_kcals)
        std = np.std(total_kcals)

        self.stdout.write(self.style.SUCCESS(
            f"{label[0]} — Mean: {mean:.2f}, Median: {median:.2f}, Std: {std:.2f}"
        ))

        # Plot histogram
        plt.figure()
        plt.hist(total_kcals, bins=50)
        plt.title(f'{label[0]} - Total Daily Kcal Distribution')
        plt.xlabel('Total kcal')
        plt.ylabel('Frequency')
        plt.grid(True)
        plt.tight_layout()
        filename = f"{label[0].lower().replace(' ', '_')}_daily_kcal_histogram.png"
        plt.savefig(filename)
        self.stdout.write(f"Saved histogram as {filename}")

    def handle(self, *args, **kwargs):
        countries = [["Ireland"], ["Spain"], ["Hungary"]]
        num_samples = 10_000_000

        for country in countries:
            self.stdout.write(f"\nSampling for {country}...")
            self.sample_and_analyze(label=country, country=country, num_samples=num_samples)

        self.stdout.write(f"\nSampling for All countries...")
        self.sample_and_analyze(label='All Countries', country=None, num_samples=num_samples)
