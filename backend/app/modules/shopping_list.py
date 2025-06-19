"""Module providing a function printing python version."""
#from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from ..models import Proximate, Dish, Meal, UserProfile, NP, NPItem
from rest_framework.response import Response
from django.db.models import Q
from collections import defaultdict


@api_view(['PUT'])
def remove_from_shopping_list(request, user_id, week_monday):
    '''
    Function that will save each meal in the shopping list.
    '''

    # Check the request method.
    if request.method != 'PUT':
        return JsonResponse({"error": "No PUT request."}, status=400)
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({'error': f"No user with this user id:{user_id}"}, status=400)
    if UserProfile.objects.filter(User=user).exists():
        user_profile = UserProfile.objects.get(User=user)
    else:
        return JsonResponse({'error': "No UserProfile for this User"}, status=400)
    try:
        shopping_list_np = NP.objects.get(UserProfile=user_profile, start_date=week_monday)
    except:
        return JsonResponse({'error': "No NP for this UserProfile"}, status=400)

    # Generate a combined filter for all items in request.data
    query = Q()
    for data in request.data:
        query |= Q(meal_id=data["meal_id"], day=data["day"], meal_type=data["type"], np=shopping_list_np)

    # Perform a single bulk update
    NPItem.objects.filter(query).update(shopping_list=False)

    shopping_list_meals = NPItem.objects.filter(np=shopping_list_np, shopping_list=True)
    shopping_list = []
    for shopping_list_meal in shopping_list_meals:
        shopping_list.append({
            "week": week_monday,
            "day": shopping_list_meal.day,
            "type": shopping_list_meal.meal_type,
            "meal_id": shopping_list_meal.meal.id,
        })

    #return JsonResponse({'message': "Removed from shopping list"}, status=200)
    return JsonResponse(shopping_list, safe=False)

@api_view(['PUT'])
def add_to_shopping_list(request, user_id, week_monday):
    '''
    Function that will save each meal in the shopping list.
    '''

    # Check the request method.
    if request.method != 'PUT':
        return JsonResponse({"error": "No PUT request."}, status=400)
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({'error': f"No user with this user id:{user_id}"}, status=400)
    if UserProfile.objects.filter(User=user).exists():
        user_profile = UserProfile.objects.get(User=user)
    else:
        return JsonResponse({'error': "No UserProfile for this User"}, status=400)
    try:
        shopping_list_np = NP.objects.get(UserProfile=user_profile, start_date=week_monday)
    except:
        return JsonResponse({'error': "No NP for this UserProfile"}, status=400)

    # Generate a combined filter for all items in request.data
    query = Q()
    for data in request.data:
        query |= Q(meal_id=data["meal_id"], day=data["day"], meal_type=data["type"], np=shopping_list_np)

    # Perform a single bulk update
    NPItem.objects.filter(query).update(shopping_list=True)

    shopping_list_meals = NPItem.objects.filter(np=shopping_list_np, shopping_list=True)
    shopping_list = []
    for shopping_list_meal in shopping_list_meals:
        shopping_list.append({
            "week": week_monday,
            "day": shopping_list_meal.day,
            "type": shopping_list_meal.meal_type,
            "meal_id": shopping_list_meal.meal.id,
        })

    #return JsonResponse({'message': 'Added to shopping list'}, status=200)
    return JsonResponse(shopping_list, safe=False)


@api_view(['GET'])
def get_shopping_list(request, user_id, week_monday):
    '''
    Function that returns the whole shopping list of a specific user for all npitems
    that are their shoping_list variable are true.
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
    try:
        shopping_list_np = NP.objects.get(UserProfile=user_profile, start_date=week_monday)
    except:
        return JsonResponse({'error': "No NP for this UserProfile"}, status=400)

    shopping_list_meals = NPItem.objects.filter(np=shopping_list_np, shopping_list=True)

    shopping_list = []

    for shopping_list_meal in shopping_list_meals:
        shopping_list.append({
            "week": week_monday,
            "day": shopping_list_meal.day,
            "type": shopping_list_meal.meal_type,
            "meal_id": shopping_list_meal.meal.id,
            "meal_name": shopping_list_meal.meal.Name,
        })

    return JsonResponse(shopping_list, safe=False)


@api_view(['GET'])
def get_shopping_list_ingredients(request, user_id, week_monday):
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
        shopping_list_np = NP.objects.get(UserProfile=user_profile, start_date=week_monday)
    except:
        return JsonResponse({'error': "No NP for this UserProfile"}, status=400)

    shopping_list_meals = NPItem.objects.filter(np=shopping_list_np, shopping_list=True)

    ingredient_list = []
    quantitie_list = []
    food_group_list = []
    ingredient_id_list = []
    for np_item in shopping_list_meals:
        # for ingredient, quantity, food_group in zip(np_item.meal.Ingredients, np_item.meal.Quantities, np_item.meal.Food_Groups):
        #     print(ingredient, quantity, food_group)
        for dishes in np_item.meal.Ingredients:
            for ingredient in dishes:
                ingredient_name = Proximate.objects.get(Food_Code=ingredient).Food_Name
                ingredient_list.append(ingredient_name)
                ingredient_id_list.append(Proximate.objects.get(Food_Code=ingredient).Food_Code)
        for dishes in np_item.meal.Quantities:
            for quantity in dishes:
                quantitie_list.append(quantity)
        for dishes in np_item.meal.Food_Groups:
            for group in dishes:
                if group[0] in ["A"]:
                    food_group_list.append("Cereals and cereal products")
                elif group[0] in ["B"]:
                    food_group_list.append("Milk and milk products")
                elif group[0] in ["C"]:
                    food_group_list.append("Eggs")
                elif group[0] in ["D"]:
                    food_group_list.append("Vegetables")
                elif group[0] in ["F"]:
                    food_group_list.append("Fruit")
                elif group[0] in ["G"]:
                    food_group_list.append("Nuts and seeds")
                elif group[0] in ["H"]:
                    food_group_list.append("Herbs and spices")
                elif group[0] in ["J"]:
                    food_group_list.append("Fish and fish products")
                elif group[0] in ["M"]:
                    food_group_list.append("Meat and meat products")
                elif group[0] in ["O"]:
                    food_group_list.append("Fats and oils")
                elif group[0] in ["P"]:
                    food_group_list.append("Beverages")
                elif group[0] in ["Q"]:
                    food_group_list.append("Alcoholic beverages ")
                elif group[0] in ["S"]:
                    food_group_list.append("Sugars, preserves and snacks")
                elif group[0] in ["W"]:
                    food_group_list.append("Soups, sauces and miscellaneous foods")
                else:
                    food_group_list.append("Other")

    data = []

    for ingredient, quantity, food_group, ingredient_id in zip(ingredient_list, quantitie_list, food_group_list, ingredient_id_list):
        data.append({
            "name": ingredient,
            "category": food_group,
            "quantity": quantity,
            "meal_id": ingredient_id,
        })

    # Step 1: Use a tuple of (meal_id, name, category) as the key
    merged = defaultdict(float)

    for item in data:
        key = (item['meal_id'], item['name'], item['category'])
        merged[key] += item['quantity']

    # Step 2: Convert back to list of dictionaries
    merged_list = [
        {'meal_id': ingredient_id, 'name': name, 'category': category, 'quantity': quantity}
        for (ingredient_id, name, category), quantity in merged.items()
    ]

    return JsonResponse(merged_list, safe=False)