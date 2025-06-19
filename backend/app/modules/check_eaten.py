"""Module providing a function printing python version."""
#from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from ..models import Dish, Meal, UserProfile, NP, NPItem
from rest_framework.response import Response
from django.db.models import Q


@api_view(['PUT'])
def remove_from_check_eaten_list(request, user_id, week_monday):
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
        check_eaten_list_np = NP.objects.get(UserProfile=user_profile, start_date=week_monday)
    except:
        return JsonResponse({'error': "No NP for this UserProfile"}, status=400)

    # Generate a combined filter for all items in request.data
    query = Q()
    for data in request.data:
        query |= Q(meal_id=data["meal_id"], day=data["day"], meal_type=data["type"], np=check_eaten_list_np)

    # Perform a single bulk update
    NPItem.objects.filter(query).update(checked=False)
    
    check_eaten_list_meals = NPItem.objects.filter(np=check_eaten_list_np, checked=True)
    check_eaten_list = []

    for check_eaten_list_meal in check_eaten_list_meals:
        check_eaten_list.append({
            "week": week_monday,
            "day": check_eaten_list_meal.day,
            "type": check_eaten_list_meal.meal_type,
            "meal_id": check_eaten_list_meal.meal.id,
        })

    return JsonResponse(check_eaten_list, safe=False)

@api_view(['PUT'])
def add_to_check_eaten_list(request, user_id, week_monday):
    '''
    Function that will save each meal in the check_eaten list.
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
        check_eaten_list_np = NP.objects.get(UserProfile=user_profile, start_date=week_monday)
    except:
        return JsonResponse({'error': "No NP for this UserProfile"}, status=400)

    # Generate a combined filter for all items in request.data
    query = Q()
    for data in request.data:
        query |= Q(meal_id=data["meal_id"], day=data["day"], meal_type=data["type"], np=check_eaten_list_np)

    # Perform a single bulk update
    NPItem.objects.filter(query).update(checked=True)

    check_eaten_list_meals = NPItem.objects.filter(np=check_eaten_list_np, checked=True)
    check_eaten_list = []

    for check_eaten_list_meal in check_eaten_list_meals:
        check_eaten_list.append({
            "week": week_monday,
            "day": check_eaten_list_meal.day,
            "type": check_eaten_list_meal.meal_type,
            "meal_id": check_eaten_list_meal.meal.id,
        })

    return JsonResponse(check_eaten_list, safe=False)


@api_view(['GET'])
def get_check_eaten_list(request, user_id, week_monday):
    '''
    Function that returns the whole check_eaten list of a specific user for all NPItem
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
        check_eaten_list_np = NP.objects.get(UserProfile=user_profile, start_date=week_monday)
    except:
        return JsonResponse({'error': "No NP for this UserProfile"}, status=400)
    
    check_eaten_list_meals = NPItem.objects.filter(np=check_eaten_list_np, checked=True)

    check_eaten_list = []

    for check_eaten_list_meal in check_eaten_list_meals:
        check_eaten_list.append({
            "week": week_monday,
            "day": check_eaten_list_meal.day,
            "type": check_eaten_list_meal.meal_type,
            "meal_id": check_eaten_list_meal.meal.id,
        })

    return JsonResponse(check_eaten_list, safe=False)