"""Module providing a function printing python version."""
import datetime
from datetime import date, timedelta
import itertools
import random
import time
#import numpy as np
#from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from ..models import Meal, UserProfile, NP, NPItem
from .nps import _filtering, _get_five_meals, _process, daily_dataframe_transform, weekly_dataframe_transform, print_best_week
import json


def calculate_characteristics(sex, age, height, weight, pal, target_weight, goal, target_goal):
    # Calculate user's BMI based on user's weight and height.
    bmi = weight / ((height/100) ** 2)

     # Calculate BMR
    # Males (aged 18–30): BMR (in kcal) = 14.4 × Body Mass (in kg) + 3.13 × Height (in cm) + 113
    # Females (aged 18–30): BMR (in kcal) = 10.4 × Body Mass (in kg) + 6.15 × Height (in cm) – 282
    # Calculation of bmr based on sex and age.
    if sex in "Male, male":
        if 0 < age <= 3:
            bmr = 28.2 * weight + 8.59 * height - 371
        elif 3 < age <= 10:
            bmr = 15.1 * weight + 7.42 * height + 306
        elif 10 < age <= 18:
            bmr = 15.6 * weight + 2.66 * height + 299
        elif 18 < age <= 30:
            bmr = 14.4 * weight + 3.13 * height + 113
        elif 30 < age <= 60:
            bmr = 11.4 * weight + 5.41 * height - 137
        else:
            bmr = 11.4 * weight + 5.41 * height - 256
    elif sex in "Female, female":
        if 0 < age <= 3:
            bmr = 30.4 * weight + 7.03 * height - 287
        elif 3 < age <= 10:
            bmr = 15.9 * weight + 2.10 * height + 349
        elif 10 < age <= 18:
            bmr = 9.4 * weight + 2.49 * height + 462
        elif 18 < age <= 30:
            bmr = 10.4 * weight + 6.15 * height - 282
        elif 30 < age <= 60:
            bmr = 8.18 * weight + 5.02 * height - 116
        else:
            bmr = 8.52 * weight + 4.21 * height + 107
    else:
        return None

    # Calculate user's energy intake based user's target_weight (that means how mutch kgs
    # the user wants to gain or lose), and target_goal (how fast to achieve the target_weight.
    # There are 2 gears, Normal which is +-500 kcal and Intence which is +-750 kcal).
    if target_weight < weight:
        if target_goal == "normal":
            energy_intake = bmr * pal - 500
        elif target_goal == "fast":
            energy_intake = bmr * pal - 750
        else:
            return None
    elif target_weight == weight:
        energy_intake = bmr * pal
    elif target_weight > weight:
        if target_goal == "normal":
            energy_intake = bmr * pal + 500
        elif target_goal == "fast":
            energy_intake = bmr * pal + 750
        else:
            return None
    else:
        return None

    return bmi, bmr, energy_intake


def update_user_profile_logic(data):
    try:
        # Calculate characteristics
        current_year = datetime.datetime.now().year
        age = current_year - data["yob"]
        pal_dict = {"sedentary": 1.4, "moderately": 1.6, "active": 1.8, "very_active": 2.0}
        bmi, bmr, energy_intake = calculate_characteristics(
            data["sex"], age,
            float(data["height"]),
            float(data["weight"]),
            pal_dict[data["PAL"]],
            float(data["target_weight"]),
            data["goal"],
            data["targetGoal"]
        )
        return energy_intake, bmi, bmr, data
    except:
        return None, None, None, None


@api_view(['PUT'])
def update_user_profile(request, user_id):
    # Check the request method.
    if request.method != 'PUT':
        return JsonResponse({"error": "No GET request."}, status=400)
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({"error": f"No User found for id: {user_id}"}, status=400)
    if UserProfile.objects.get(User=user):
        user_profile = UserProfile.objects.get(User=user)
    else:
        return JsonResponse({"error", f"No UserProfile user for User: {user.id}"}, status=400)

    current_year = datetime.datetime.now().year  # Get current year
    data = request.data
    # Calculate user's age based on yob and current year.
    age = current_year - data["yob"]

    pal_dict = {  # Dictionary to get the corresponding pal value.
        "sedentary": 1.4,
        "moderately": 1.6,
        "active": 1.8,
        "very_active": 2.0,
    }

    bmi, bmr, energy_intake = calculate_characteristics(data["sex"], age, int(data["height"]), int(data["weight"]),\
        pal_dict[data["PAL"]], int(data["target_weight"]), data["goal"], data["targetGoal"])

    user_profile.Energy_Intake = energy_intake
    user_profile.Bmi = bmi
    user_profile.Bmr = bmr
    user_profile.Height = data["height"]
    user_profile.Weight = data["weight"]
    user_profile.Pal = pal_dict[data["PAL"]]
    user_profile.Preferences = data["dietaryPreferences"]
    user_profile.Allergies = data["allergies"]
    user_profile.Selected_Cuisines = data["selectedCuisines"]
    user_profile.Target_Weight = data["target_weight"]
    user_profile.Goal = data["goal"]
    user_profile.TargetGoal = data["targetGoal"]
    user_profile.save()

    return JsonResponse({'message': 'User profile sccesfully updated.'}, status=200)


@api_view(['PUT'])
def update_user_main_screen(request, user_id):
    print("MPHKAA")
    # Check the request method.
    if request.method != 'PUT':
        return JsonResponse({"error": "No GET request."}, status=400)
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({"error": f"No User found for id: {user_id}"}, status=400)
    if UserProfile.objects.get(User=user):
        user_profile = UserProfile.objects.get(User=user)
    else:
        return JsonResponse({"error", f"No UserProfile user for User: {user.id}"}, status=400)

    data = json.loads(request.body)
    print(data)
    print(data.get('main_screen'))
    print(user_profile.Main_screen)
    user_profile.Main_screen = data.get('main_screen')
    user_profile.save()

    return JsonResponse({'message': 'Main screen sccesfully updated.'}, status=200)



@api_view(['PUT'])
def update_current_week_nps(request, user_id, week_monday, week_sunday):
    '''
    The create_nps function is responsible for genereting appropriate weekly nutritional meal plan
    based on a user's profile. It takes as argument the user's id, start of the week (monday), and
    end of the week (sunday) in the form of YY/MM/DD. After the correct generation of a weekly NP
    it return a status 200 to the frondend.
    '''

    # Check the request method.
    if request.method != 'PUT':
        return JsonResponse({"error": "No PUT request."}, status=400)
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

    print(user_profile.Energy_Intake)
    print(user_profile.Weight)
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

    print("---------------")
    print(weekly_results[0])
    print("---------------")

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
            week = user_np[len(user_np)-1].week
    except ImportError:
        return JsonResponse({'error': f'Could not get the nps for user:{user_id}.'}, status=400)
    print("----->", week)
    # Save the new generated weekly meal plan.
    # Create an NP for this user for this week.
    np = NP.objects.get(UserProfile=user_profile, start_date=week_monday, end_date=week_sunday, week=week)

    # Delete the np.
    np.delete()

    # Create a new np with the new generated weekly meal plans
    np = NP.objects.create(UserProfile=user_profile, user_energy_intake=user_profile.Energy_Intake, start_date=week_monday, end_date=week_sunday, week=week)

    # Keep the days of the week into a list.
    days = ["Monday", "Tuesday", "Wednesday",
           "Thursday", "Friday", "Saturday", "Sunday"]
    # Keep the meal types into a list.
    meal_types = ["Breakfast", "Morning Snack",
                 "Lunch", "Afternoon Snack", "Dinner"]
    # Iterate through the final, weekly meals.
    for i, day in enumerate(days):
        for j, meal_type in enumerate(meal_types):
            npitem = NPItem.objects.create(np=np,
                                            meal=Meal.objects.get(id=weekly_results[0]["meals"][i][j]),
                                            day=day,
                                            meal_type=meal_type)
            #print(np.id, npitem.id, day, Meal.objects.get(id=weekly_results[0]["meals"][i][j]), meal_type, ratio_list[i])

    return JsonResponse({'message': 'Weekly np updated succesfully.'}, status=200)

