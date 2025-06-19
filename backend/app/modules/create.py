"""Module providing a function printing python version."""
import time
import datetime
import numpy as np
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from ..models import UserProfile, UserAchievements
from .update import calculate_characteristics

@api_view(['POST'])
def create_user_profile(request, user_id):
    '''
    The create_user_profile function is responcible for saving the user's information such as name,
    year of bearth, etc. For this to be done some attributes are coming from the frontend where the
    other attributs are calculated here in this funciton.
    '''

    # Check the request method.
    if request.method != "POST":
        return JsonResponse({'error': 'No POST request.'}, status=400)
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({'error': f"No User with User id:{user_id}"}, status=400)

    data = request.data  # Fetch the data from the frontend.

    # Attributes come from the frontend.
    role = data["role"] # Role either Tester of Pilot.
    pilot_country = data["country"] # In case of Pilot we get the country.
    sex = data["sex"]  # Save the sex.
    yob = int(data["yob"])  # Save the year of birth.
    height = int(data["height"]) # Height in cm.
    weight = int(data["weight"]) # Save the weight which is in kg.
    pal = data["PAL"]  # Save the pal which is a string.
    target_weight = int(data["target_weight"]) # Save the target weight on kg.
    goal = data["goal"] # Save how fast to reach the target goal. Normal or Rapid.
    target_goal = data["targetGoal"] # Save the amound of kcals to losse of gain daily.
    allergies = data["allergies"]  # Save the allergies which is a string.
    preferences = data["dietaryPreferences"] # Save the user's preferences.
    selected_cuisines = data["selectedCuisines"]  # Save the country which is a string.

    # Attributes calculated here.
    current_year = datetime.datetime.now().year  # Get current year
    # Calculate user's age based on yob and current year.
    age = current_year - yob

    pal_dict = {  # Dictionary to get the corresponding pal value.
        "sedentary": 1.4,
        "moderately": 1.6,
        "active": 1.8,
        "very_active": 2.0,
    }
    pal = pal_dict[pal]

    bmi, bmr, energy_intake = calculate_characteristics(sex, age, height, weight, pal, target_weight, goal, target_goal)
    if bmi is None:
        JsonResponse({'error': f'Error in calculate_characteristics.'}, status=400)

    # Create the UserProfile user.
    UserProfile.objects.create(User=user, Role=role, Pilot_Country=pilot_country,
                                Sex=sex, Yob=yob, Age=age, Height=height, Weight=weight,
                                Pal=pal, Bmi=bmi, Bmr=bmr, Energy_Intake=energy_intake,
                                Target_Weight=target_weight, Goal=goal, TargetGoal=target_goal,
                                Allergies=allergies, Preferences=preferences,
                                Selected_Cuisines=selected_cuisines)

    return JsonResponse({'message': 'User created.'}, status=200)
