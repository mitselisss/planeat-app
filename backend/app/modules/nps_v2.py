# modules/nps.py

from app.models import Meal, NP
from app.management.commands.np_generator_v4 import return_best_plan
from django.http import JsonResponse
from collections import defaultdict
from collections import Counter

def create_nutrition_plan(user_profile):
    # Step 1: Prepare user settings
    user_settings = {
        'energy_intake': user_profile.Energy_Intake,
        'base_energy': 2500,  # Or static like 2500
        'preference': user_profile.Preferences,
        'allergy': user_profile.Allergies,
        'cuisine': user_profile.Selected_Cuisines,
        'sex': user_profile.Sex,
        'a/a': 0,
    }

    # Step 2: Generate plan
    result = return_best_plan(user_settings)
    return result
