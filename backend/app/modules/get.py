"""Module providing a function printing python version."""
#from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from ..models import Dish, Meal, Proximate, UserProfile, NP, NPItem
from rest_framework.response import Response
from collections import defaultdict

@api_view(['GET'])
def get_daily_np(request, user_id, week_monday, day):
    '''
    Function that returns the daily np for a specific user, date of current
    monday and current day
    '''

    # Check the request method.
    if request.method != 'GET':
        return JsonResponse({"error": "No GET request."}, status=400)
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({'error': f"No user with this user id:{user_id}"}, status=400)
    if UserProfile.objects.filter(User=user).exists():
        user_profile = UserProfile.objects.get(User=user)
    else:
        return JsonResponse({'error': "No UserProfile for this User"}, status=400)

    daily_np = NP.objects.filter(UserProfile=user_profile, start_date=week_monday)
    if not daily_np.exists():
        return JsonResponse({'error': "No NPs for this UserProfile"}, status=400)

    # Keep only the first instance and delete the rest
    if daily_np.count() > 1:
        daily_np.exclude(id=daily_np.first().id).delete()

    # Fetch the first instance again to avoid QuerySet issues
    daily_np = daily_np.first()
    daily_meals = NPItem.objects.filter(np=daily_np, day=day)
    if not daily_meals.exists():
        return JsonResponse({'error': f"No daily meals found for this NP {daily_np} and day {day}"}, status=400)

    print(daily_meals)
    # Create dictionary for meal details
    daily_meals_info = {}

    # Dynamically fetch dish fields
    for i, np in enumerate(daily_meals):
        daily_meals_info["meal_"+str(i)] = {
            "meal_id": np.meal.id,
            "meal_name": np.meal.Name,
            "meal_type": np.meal_type,
            "valid": np.valid_day,
            "country": np.meal.Country
        }

    return JsonResponse(daily_meals_info)


@api_view(['GET'])
def get_meal_info(request, meal_id):
    '''
    Function that returns the mean information for a specifi user.
    '''

    # Check the request method.
    if request.method != 'GET':
        return JsonResponse({"error": "No GET request."}, status=400)

    meal = Meal.objects.get(id=meal_id)
    meal_info = {}
    meal_info["meal_id"] = meal.id
    meal_info["meal_name"] = meal.Name
    meal_info["meal_description"] = meal.Description
    meal_info["Total_Energy"] = meal.Total_Energy
    meal_info["Total_Fat"] = meal.Total_Fat
    meal_info["Total_Protein"] = meal.Total_Protein
    meal_info["Total_Carbs"] = meal.Total_Carbs
    meal_info["ingredient_info"] = {}

    quantities_list = meal.Quantities
    ingredients_list = meal.Ingredients
    count = 0
    for i, dish in enumerate(meal.Ingredients):
        for j, cofid in enumerate(dish):
            incredient = Proximate.objects.get(Food_Code=cofid)
            meal_info["ingredient_info"]["ingredient_"+str(count)] = {
                "ingredient_food_code": cofid,
                "ingredient_name": incredient.Food_Name,
                "quantity": quantities_list[i][j],
                "kcal": quantities_list[i][j] * incredient.Energy / 100,
                "protein": quantities_list[i][j] * incredient.Protein / 100,
                "fat": quantities_list[i][j] * incredient.Fat / 100,
                "carbs": quantities_list[i][j] * incredient.Carbohydrate / 100,
            }
            count += 1

    return JsonResponse(meal_info)


@api_view(['GET'])
def get_dishes_info(request, meal_id):
    '''
    Function that returns the dishes information for a specific user.
    '''
    meal = Meal.objects.get(id=meal_id)
    dishes = meal.Dishes

    # Create a dictionary to store dishes' information.
    dishes_info = {}

    for idx, (dish, ingredients, quantities) in enumerate(zip(meal.Dishes, meal.Ingredients, meal.Quantities)):
        dishes_info["dish_"+str(idx+1)] = {
            "dish_id": dish,
            "dish_name": Dish.objects.get(id=dish).Description,
            "dish_recipe": Dish.objects.get(id=dish).Recipe if Dish.objects.get(id=dish).Recipe != "-3" else "",
            "Total_Energy": Dish.objects.get(id=dish).Total_Energy,
            "Total_Fat": Dish.objects.get(id=dish).Total_Fat,
            "Total_Carbs": Dish.objects.get(id=dish).Total_Carbs,
            "Total_Protein": Dish.objects.get(id=dish).Total_Protein,
            "ingredient_info": {}
        }

        count = 0
        for ingredient, quantity in zip(ingredients, quantities):
            incredient = Proximate.objects.get(Food_Code=ingredient)
            dishes_info["dish_"+str(idx+1)]["ingredient_info"]["ingredient_"+str(count)] = {
                "ingredient_food_code": incredient.Food_Code,
                "ingredient_name": incredient.Food_Name,
                "quantity": quantity,
                "kcal": quantity * incredient.Energy / 100,
                "protein": quantity * incredient.Protein / 100,
                "fat": quantity * incredient.Fat / 100,
                "carbs": quantity * incredient.Carbohydrate / 100,
            }
            count += 1

    return Response(dishes_info)


@api_view(['GET'])
def get_user_weeks(request, user_id):
    '''
    This function returns the weeks that have nutrition plans for a specific user.
    '''

    # Check if the Django User for the specific user_id.
    if User.objects.get(id=user_id):
        # Get the Django User for the specific user_id.
        user = User.objects.get(id=user_id)
    else:
        # Return and error and status 400.
        return JsonResponse({"error", "No Django User with userid:", {user_id}}, status=400)
    # Check if the UserProfile for the specific User.
    if UserProfile.objects.filter(User=user):
        # Get the UserProfile for the specific User.
        user_profile = UserProfile.objects.get(User=user)
    else:
        # Return and error and status 400.
        return JsonResponse({"error": "No UserProfile found for userid: {user_id}"}, status=400)
    # Check if the specific user has nutrition plan(s).
    if NP.objects.filter(UserProfile=user_profile):
        # Get the nutrition plan(s) of the user.
        user_nps = NP.objects.filter(UserProfile=user_profile)
        user_weeks = {}  # Declare a dictionary to hold the week(s).

        # Iterate through the nutrition plan(s) of the user.
        for i, user in enumerate(user_nps):
            start_date = user.start_date  # Get the start date of the NP.
            start_day = start_date.day  # Save the day (DD)
            start_month = start_date.month  # Save the month (MM)
            start_year = start_date.year  # Save the year (YY)

            end_date = user.end_date  # Get the end date of the NP
            end_day = end_date.day  # Save the day (DD)
            end_month = end_date.month  # Save the month (MM)
            end_year = end_date.year  # Save the year (YY)

            # for each NP create a user_weeks{} dictionary with the number of the week,
            # start date and end date.
            user_weeks[f"Week_{i + 1}"] = {
                "week": i+1,
                "start_date": f"{start_day:02d}-{start_month:02d}-{start_year}",
                "end_date": f"{end_day:02d}-{end_month:02d}-{end_year}",
            }

        # Return the user's weeks to the front end alongside a status 200.
        return JsonResponse(user_weeks, status=200)
    else:
        # There is no user with such userid. Return an error alongside a status 400.
        return JsonResponse({"error": "No NP for user:, {user_id}"}, status=400)


@api_view(['GET'])
def check_weekly_np(request, user_id, week_monday, week_sunday):
    """
    Function that checks if a specific user has a weekly np for a week time frame.
    """

    # Check if the Django User exists for the paricullar id.
    if User.objects.filter(id=user_id).exists():
        # Given the user id retrieve the corresponding user from the Djando User model.
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({"error": f"No User found for id: {user_id}"}, status=400)
    # Check if the UserProfile user exists.
    if UserProfile.objects.get(User=user):
        # Having the Django User we retrieve the corresponding user from the UserProfile model.
        user_profile = UserProfile.objects.get(User=user)
        # From the UserProfile we retrieve any info of this model like Energy_Intake.
        # energy_intake = user_profile.Energy_Intake
        # meals = Meal.objects.all() # Retrieve all the meals from the meals table.
    else:
        return JsonResponse({"error", f"No UserProfile user for User: {user.id}"}, status=400)
    # Check if there is already a weekly meal plan for this user for this week.
    if NP.objects.filter(UserProfile=user_profile, start_date=week_monday, end_date=week_sunday).exists():
        return JsonResponse({"message": "Weekly NP exists."}, status=200)
    return JsonResponse({"error": "Weekly NP does not exist."}, status=400)


@api_view(['GET'])
def get_nutritional_info(request, user_id, week_monday):
    # Check the request method.
    if request.method != 'GET':
        return JsonResponse({"error": "No GET request."}, status=400)
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({"error": f"No User found for id: {user_id}"}, status=400)
    if UserProfile.objects.get(User=user):
        user_profile = UserProfile.objects.get(User=user)
    else:
        return JsonResponse({"error", f"No UserProfile user for User: {user.id}"}, status=400)

    nps = NP.objects.get(UserProfile=user_profile, start_date=week_monday)
    np_items = NPItem.objects.filter(np=nps)

    nutritional_dict = {
        "user_enegy_intake": nps.user_energy_intake,
    }

    for i in range(0, len(np_items), 5):
        breakfast = np_items[i].meal
        morning_snack = np_items[i+1].meal
        lunch = np_items[i+2].meal
        afternoon_snack = np_items[i+3].meal
        dinner = np_items[i+4].meal

        # Macro info
        total_kcal = breakfast.Total_Energy + morning_snack.Total_Energy + lunch.Total_Energy + afternoon_snack.Total_Energy + dinner.Total_Energy
        total_protein = breakfast.Total_Protein + morning_snack.Total_Protein + lunch.Total_Protein + afternoon_snack.Total_Protein + dinner.Total_Protein
        total_fat = breakfast.Total_Fat + morning_snack.Total_Fat + lunch.Total_Fat + afternoon_snack.Total_Fat + dinner.Total_Fat
        total_carbs = breakfast.Total_Carbs + morning_snack.Total_Carbs + lunch.Total_Carbs + afternoon_snack.Total_Carbs + dinner.Total_Carbs

        # Micro info
        Total_Calcium = breakfast.Total_Calcium + morning_snack.Total_Calcium + lunch.Total_Calcium + afternoon_snack.Total_Calcium + dinner.Total_Calcium
        Total_Iron = breakfast.Total_Iron + morning_snack.Total_Iron + lunch.Total_Iron + afternoon_snack.Total_Iron + dinner.Total_Iron
        Total_Folate = breakfast.Total_Folate + morning_snack.Total_Folate + lunch.Total_Folate + afternoon_snack.Total_Folate + dinner.Total_Folate

        nutritional_dict["day_"+str(int(i/5)+1)] = {
            "macro": {
                "total_kcal": total_kcal,
                "total_protein": total_protein,
                "total_fat": total_fat,
                "total_carbs": total_carbs,
            },
            "micro": {
                "Total_Calcium": Total_Calcium,
                "Total_Iron": Total_Iron,
                "Total_Folate": Total_Folate,
            },
        }

    return Response(nutritional_dict)


@api_view(['GET'])
def get_weekly_food_user_goal_categories(request, user_id, week_monday):
    # Check the request method.
    if request.method != 'GET':
        return JsonResponse({"error": "No GET request."}, status=400)
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({"error": f"No User found for id: {user_id}"}, status=400)
    if UserProfile.objects.get(User=user):
        user_profile = UserProfile.objects.get(User=user)
    else:
        return JsonResponse({"error", f"No UserProfile user for User: {user.id}"}, status=400)

    nps = NP.objects.get(UserProfile=user_profile, start_date=week_monday)
    np_items = NPItem.objects.filter(np=nps)


    food_group_dict = {
        "Meat": [0, 0],
        "Plant_protein": [0, 0],
        "Vegetables": [0, 0],
        "Fruit": [0, 0],
        "Dairy": [0, 0],
        "Nuts_and_seeds": [0, 0],
        "Fish": [0, 0],
    }

    for np_item in np_items:
        meal = np_item.meal
        for key, value in food_group_dict.items():
            food_group_dict[key][0] += getattr(meal, key)

    food_group_dict_experts = { # experts
        # exclude all foods from CoFID food group codes MI and MIG (processed meats)
        "Meat": ["MA", "MAA", "MAC", "MAE", "MAG", "MAI", "MC", "MCA", "MCC", "MCE", "MCG", "MI",
                 "MCK", "MCM", "MCO", "ME", "MEA", "MEC", "MEE", "MG", "MBG", "MI", "MIG", "MR"],
        "Plant_protein": ["DB"],
        "Vegetables": ["DF", "DG", "DI", "DR"],
        # with no more than 1 serving per day from FC
        "Fruit": ["F", "FA", "FC"],
        # with no more than 1 serving of BL per day
        "Dairy": ["BA", "BC", "BL", "BN"],
        "Nuts_and_seeds": ["G", "GA"],
        # with at least 1 serving per week from JC
        "Fish": ["J", "JA", "JC", "JK", "JM", "JR"],
    }

    for i, np_item in enumerate(np_items):
        food_groups = np_item.meal.Food_Groups_Counter
        for group, counter, quantity in food_groups:
            for experts_group, mcane_group in food_group_dict_experts.items():
                if group in mcane_group:
                    food_group_dict[experts_group][0] += counter
                    food_group_dict[experts_group][1] += quantity

    return Response(food_group_dict)


@api_view(['GET'])
def get_weekly_food_categories(request, user_id, week_monday):
    # Check the request method.
    if request.method != 'GET':
        return JsonResponse({"error": "No GET request."}, status=400)
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({"error": f"No User found for id: {user_id}"}, status=400)
    if UserProfile.objects.get(User=user):
        user_profile = UserProfile.objects.get(User=user)
    else:
        return JsonResponse({"error", f"No UserProfile user for User: {user.id}"}, status=400)

    nps = NP.objects.get(UserProfile=user_profile, start_date=week_monday)
    np_items = NPItem.objects.filter(np=nps)


    food_group_dict = {
        "Cereals and cereal products": [0, 0],
        "Milk and milk products": [0, 0],
        "Eggs": [0, 0],
        "Vegetables": [0, 0],
        "Fruit": [0, 0],
        "Nuts and seeds": [0, 0],
        "Herbs and spices": [0, 0],
        "Fish and fish products": [0, 0],
        "Meat and meat products": [0, 0],
        "Fats and oils": [0, 0],
        "Beverages": [0, 0],
        "Alcoholic beverages": [0, 0],
        "Sugars, preserves and snacks": [0, 0],
        "Soups, sauces and miscellaneous foods": [0, 0],
        "Other":  [0, 0],

        # "Meat": [0, 0],
        # "Plant_protein": [0, 0],
        # "Vegetables": [0, 0],
        # "Fruit": [0, 0],
        # "Dairy": [0, 0],
        # "Nuts_and_seeds": [0, 0],
        # "Fish": [0, 0],
    }

    # for np_item in np_items:
    #     meal = np_item.meal
    #     for key, value in food_group_dict.items():
    #         food_group_dict[key][0] += getattr(meal, key)

    # food_group_dict_experts = { # experts
    #     # exclude all foods from CoFID food group codes MI and MIG (processed meats)
    #     "Meat": ["MA", "MAA", "MAC", "MAE", "MAG", "MAI", "MC", "MCA", "MCC", "MCE", "MCG", "MI",
    #              "MCK", "MCM", "MCO", "ME", "MEA", "MEC", "MEE", "MG", "MBG", "MI", "MIG", "MR"],
    #     "Plant_protein": ["DB"],
    #     "Vegetables": ["DF", "DG", "DI", "DR"],
    #     # with no more than 1 serving per day from FC
    #     "Fruit": ["F", "FA", "FC"],
    #     # with no more than 1 serving of BL per day
    #     "Dairy": ["BA", "BC", "BL", "BN"],
    #     "Nuts_and_seeds": ["G", "GA"],
    #     # with at least 1 serving per week from JC
    #     "Fish": ["J", "JA", "JC", "JK", "JM", "JR"],
    # }

    for i, np_item in enumerate(np_items):
        food_groups = np_item.meal.Food_Groups_Counter
        for group, counter, quantity in food_groups:
            if group[0] in ["A"]:
                food_group_dict["Cereals and cereal products"][0] += counter
                food_group_dict["Cereals and cereal products"][1] += quantity
            elif group[0] in ["B"]:
                food_group_dict["Milk and milk products"][0] += counter
                food_group_dict["Milk and milk products"][1] += quantity
            elif group[0] in ["C"]:
                food_group_dict["Eggs"][0] += counter
                food_group_dict["Eggs"][1] += quantity
            elif group[0] in ["D"]:
                food_group_dict["Vegetables"][0] += counter
                food_group_dict["Vegetables"][1] += quantity
            elif group[0] in ["F"]:
                food_group_dict["Fruit"][0] += counter
                food_group_dict["Fruit"][1] += quantity
            elif group[0] in ["G"]:
                food_group_dict["Nuts and seeds"][0] += counter
                food_group_dict["Nuts and seeds"][1] += quantity
            elif group[0] in ["H"]:
                food_group_dict["Herbs and spices"][0] += counter
                food_group_dict["Herbs and spices"][1] += quantity
            elif group[0] in ["J"]:
                food_group_dict["Fish and fish products"][0] += counter
                food_group_dict["Fish and fish products"][1] += quantity
            elif group[0] in ["M"]:
                food_group_dict["Meat and meat products"][0] += counter
                food_group_dict["Meat and meat products"][1] += quantity
            elif group[0] in ["O"]:
                food_group_dict["Fats and oils"][0] += counter
                food_group_dict["Fats and oils"][1] += quantity
            elif group[0] in ["P"]:
                food_group_dict["Beverages"][0] += counter
                food_group_dict["Beverages"][1] += quantity
            elif group[0] in ["Q"]:
                food_group_dict["Alcoholic beverages"][0] += counter
                food_group_dict["Alcoholic beverages"][1] += quantity
            elif group[0] in ["S"]:
                food_group_dict["Sugars, preserves and snacks"][0] += counter
                food_group_dict["Sugars, preserves and snacks"][1] += quantity
            elif group[0] in ["W"]:
                food_group_dict["Soups, sauces and miscellaneous foods"][0] += counter
                food_group_dict["Soups, sauces and miscellaneous foods"][1] += quantity
            else:
                food_group_dict["Other"][0] += counter
                food_group_dict["Other"][1] += quantity

    return Response(food_group_dict)


@api_view(['GET'])
def get_daily_food_user_goal_categories(request, user_id, week_monday, day):
    # Check the request method.
    if request.method != 'GET':
        return JsonResponse({"error": "No GET request."}, status=400)
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({"error": f"No User found for id: {user_id}"}, status=400)
    if UserProfile.objects.get(User=user):
        user_profile = UserProfile.objects.get(User=user)
    else:
        return JsonResponse({"error", f"No UserProfile user for User: {user.id}"}, status=400)

    nps = NP.objects.get(UserProfile=user_profile, start_date=week_monday)
    np_items = NPItem.objects.filter(np=nps, day=day)

    food_group_dict = {
        "Meat": [0, 0],
        "Plant_protein": [0, 0],
        "Vegetables": [0, 0],
        "Fruit": [0, 0],
        "Dairy": [0, 0],
        "Nuts_and_seeds": [0, 0],
        "Fish": [0, 0],
    }

    for np_item in np_items:
        meal = np_item.meal
        for key, value in food_group_dict.items():
            food_group_dict[key][0] += getattr(meal, key)

    dishes = ["Dish_1", "Dish_2", "Dish_3", "Dish_4", "Dish_5", "Dish_6", "Dish_7", "Dish_8"]
    quantities = ["Quantity_1", "Quantity_2", "Quantity_3", "Quantity_4", "Quantity_5", "Quantity_6", "Quantity_7", "Quantity_8", "Quantity_9", "Quantity_10"]
    cofids = ["CoFID_1", "CoFID_2", "CoFID_3", "CoFID_4", "CoFID_5", "CoFID_6", "CoFID_7", "CoFID_8", "CoFID_9", "CoFID_10"]
    food_groups = ["Meat", "Plant_protein", "Vegetables", "Fruit", "Dairy", "Nuts_and_seeds", "Fish"]

    food_group_dict_experts = { # experts
        # exclude all foods from CoFID food group codes MI and MIG (processed meats)
        "Meat": ["MA", "MAA", "MAC", "MAE", "MAG", "MAI", "MC", "MCA", "MCC", "MCE", "MCG", "MI",
                 "MCK", "MCM", "MCO", "ME", "MEA", "MEC", "MEE", "MG", "MBG", "MI", "MIG", "MR"],
        "Plant_protein": ["DB"],
        "Vegetables": ["DF", "DG", "DI", "DR"],
        # with no more than 1 serving per day from FC
        "Fruit": ["F", "FA", "FC"],
        # with no more than 1 serving of BL per day
        "Dairy": ["BA", "BC", "BL", "BN"],
        "Nuts_and_seeds": ["G", "GA"],
        # with at least 1 serving per week from JC
        "Fish": ["J", "JA", "JC", "JK", "JM", "JR"],
    }

    for np_item in np_items:
        meal = np_item.meal
        for group, counter, quantity in meal.Food_Groups_Counter:
            for experts_group, mcane_group in food_group_dict_experts.items():
                if group in mcane_group:
                    food_group_dict[experts_group][0] += counter
                    food_group_dict[experts_group][1] += quantity

    return Response(food_group_dict)


@api_view(['GET'])
def get_daily_food_categories(request, user_id, week_monday, day):
    # Check the request method.
    if request.method != 'GET':
        return JsonResponse({"error": "No GET request."}, status=400)
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({"error": f"No User found for id: {user_id}"}, status=400)
    if UserProfile.objects.get(User=user):
        user_profile = UserProfile.objects.get(User=user)
    else:
        return JsonResponse({"error", f"No UserProfile user for User: {user.id}"}, status=400)

    nps = NP.objects.get(UserProfile=user_profile, start_date=week_monday)
    np_items = NPItem.objects.filter(np=nps, day=day)

    food_group_dict = {
        "Cereals and cereal products": [0, 0],
        "Milk and milk products": [0, 0],
        "Eggs": [0, 0],
        "Vegetables": [0, 0],
        "Fruit": [0, 0],
        "Nuts and seeds": [0, 0],
        "Herbs and spices": [0, 0],
        "Fish and fish products": [0, 0],
        "Meat and meat products": [0, 0],
        "Fats and oils": [0, 0],
        "Beverages": [0, 0],
        "Alcoholic beverages": [0, 0],
        "Sugars, preserves and snacks": [0, 0],
        "Soups, sauces and miscellaneous foods": [0, 0],
        "Other":  [0, 0],

        # "Meat": [0, 0],
        # "Plant_protein": [0, 0],
        # "Vegetables": [0, 0],
        # "Fruit": [0, 0],
        # "Dairy": [0, 0],
        # "Nuts_and_seeds": [0, 0],
        # "Fish": [0, 0],
    }

    # for np_item in np_items:
    #     meal = np_item.meal
    #     for key, value in food_group_dict.items():
    #         food_group_dict[key][0] += getattr(meal, key)

    dishes = ["Dish_1", "Dish_2", "Dish_3", "Dish_4", "Dish_5", "Dish_6", "Dish_7", "Dish_8"]
    quantities = ["Quantity_1", "Quantity_2", "Quantity_3", "Quantity_4", "Quantity_5", "Quantity_6", "Quantity_7", "Quantity_8", "Quantity_9", "Quantity_10"]
    cofids = ["CoFID_1", "CoFID_2", "CoFID_3", "CoFID_4", "CoFID_5", "CoFID_6", "CoFID_7", "CoFID_8", "CoFID_9", "CoFID_10"]
    food_groups = ["Meat", "Plant_protein", "Vegetables", "Fruit", "Dairy", "Nuts_and_seeds", "Fish"]

    # food_group_dict_experts = { # experts
    #     # exclude all foods from CoFID food group codes MI and MIG (processed meats)
    #     "Meat": ["MA", "MAA", "MAC", "MAE", "MAG", "MAI", "MC", "MCA", "MCC", "MCE", "MCG", "MI",
    #              "MCK", "MCM", "MCO", "ME", "MEA", "MEC", "MEE", "MG", "MBG", "MI", "MIG", "MR"],
    #     "Plant_protein": ["DB"],
    #     "Vegetables": ["DF", "DG", "DI", "DR"],
    #     # with no more than 1 serving per day from FC
    #     "Fruit": ["F", "FA", "FC"],
    #     # with no more than 1 serving of BL per day
    #     "Dairy": ["BA", "BC", "BL", "BN"],
    #     "Nuts_and_seeds": ["G", "GA"],
    #     # with at least 1 serving per week from JC
    #     "Fish": ["J", "JA", "JC", "JK", "JM", "JR"],
    # }

    for np_item in np_items:
        meal = np_item.meal
        for group, counter, quantity in meal.Food_Groups_Counter:
            if group[0] in ["A"]:
                food_group_dict["Cereals and cereal products"][0] += counter
                food_group_dict["Cereals and cereal products"][1] += quantity
            elif group[0] in ["B"]:
                food_group_dict["Milk and milk products"][0] += counter
                food_group_dict["Milk and milk products"][1] += quantity
            elif group[0] in ["C"]:
                food_group_dict["Eggs"][0] += counter
                food_group_dict["Eggs"][1] += quantity
            elif group[0] in ["D"]:
                food_group_dict["Vegetables"][0] += counter
                food_group_dict["Vegetables"][1] += quantity
            elif group[0] in ["F"]:
                food_group_dict["Fruit"][0] += counter
                food_group_dict["Fruit"][1] += quantity
            elif group[0] in ["G"]:
                food_group_dict["Nuts and seeds"][0] += counter
                food_group_dict["Nuts and seeds"][1] += quantity
            elif group[0] in ["H"]:
                food_group_dict["Herbs and spices"][0] += counter
                food_group_dict["Herbs and spices"][1] += quantity
            elif group[0] in ["J"]:
                food_group_dict["Fish and fish products"][0] += counter
                food_group_dict["Fish and fish products"][1] += quantity
            elif group[0] in ["M"]:
                food_group_dict["Meat and meat products"][0] += counter
                food_group_dict["Meat and meat products"][1] += quantity
            elif group[0] in ["O"]:
                food_group_dict["Fats and oils"][0] += counter
                food_group_dict["Fats and oils"][1] += quantity
            elif group[0] in ["P"]:
                food_group_dict["Beverages"][0] += counter
                food_group_dict["Beverages"][1] += quantity
            elif group[0] in ["Q"]:
                food_group_dict["Alcoholic beverages"][0] += counter
                food_group_dict["Alcoholic beverages"][1] += quantity
            elif group[0] in ["S"]:
                food_group_dict["Sugars, preserves and snacks"][0] += counter
                food_group_dict["Sugars, preserves and snacks"][1] += quantity
            elif group[0] in ["W"]:
                food_group_dict["Soups, sauces and miscellaneous foods"][0] += counter
                food_group_dict["Soups, sauces and miscellaneous foods"][1] += quantity
            else:
                food_group_dict["Other"][0] += counter
                food_group_dict["Other"][1] += quantity
            # for experts_group, mcane_group in food_group_dict_experts.items():
            #     if group in mcane_group:
            #         food_group_dict[experts_group][0] += counter
            #         food_group_dict[experts_group][1] += quantity

    return Response(food_group_dict)


@api_view(['GET'])
def get_user_profile(request, user_id):
    # Check the request method.
    if request.method != 'GET':
        return JsonResponse({"error": "No GET request."}, status=400)
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({"error": f"No User found for id: {user_id}"}, status=400)
    if UserProfile.objects.get(User=user):
        user_profile = UserProfile.objects.get(User=user)
    else:
        return JsonResponse({"error", f"No UserProfile user for User: {user.id}"}, status=400)

    user_info = {
        "username": user.username,
        "email": user.email,
        "role": user_profile.Role,
        "sex": user_profile.Sex,
        "yob": user_profile.Yob,
        "height": user_profile.Height,
        "weight": user_profile.Weight,
        "pal": user_profile.Pal,
        "preferences": user_profile.Preferences,
        "allergies": user_profile.Allergies,
        "cuisine": user_profile.Selected_Cuisines,
        "target_weight": user_profile.Target_Weight,
        "goal": user_profile.Goal,
        "target_goal": user_profile.TargetGoal,
        "pilot_country": user_profile.Pilot_Country,
        "main_screen": user_profile.Main_screen
    }

    return Response(user_info)


@api_view(['GET'])
def get_weekly_np(request, user_id, week_monday):
    # Check the request method.
    if request.method != 'GET':
        return JsonResponse({"error": "No GET request."}, status=400)
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({'error': f"No user with this user id:{user_id}"}, status=400)
    if UserProfile.objects.filter(User=user).exists():
        user_profile = UserProfile.objects.get(User=user)
    else:
        return JsonResponse({'error': "No UserProfile for this User"}, status=400)
    try:
        weekly_np = NP.objects.filter(UserProfile=user_profile, start_date=week_monday)
    except:
        return JsonResponse({'error': f"No NPs for this {user_profile}, for {week_monday}"}, status=400)
    # Keep only the first instance and delete the rest
    if weekly_np.count() > 1:
        weekly_np.exclude(id=weekly_np.first().id).delete()
    # Fetch the first instance again to avoid QuerySet issues
    weekly_np = weekly_np.first()
    weekly_meals = NPItem.objects.filter(np=weekly_np)

    weekly_meals_info = {
        "Monday" : {},
        "Tuesday" : {},
        "Wednesday" : {},
        "Thursday" : {},
        "Friday" : {},
        "Saturday" : {},
        "Sunday" : {},
    }

    j = 0
    for key, value in weekly_meals_info.items():
        temp = weekly_meals.filter(day=key)
        for i, t in enumerate(temp):
            weekly_meals_info[key]["meal_"+str(i)] = {
                "meal_id": t.meal.id,
                "meal_name": t.meal.Name,
                "meal_type": t.meal_type,
            }
        j += 5

    return JsonResponse(weekly_meals_info)


