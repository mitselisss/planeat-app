from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Meal, UserProfile, NP, NPItem
from app.models import UserProfile
from app.modules.nps_v2 import create_nutrition_plan
from app.modules.update import update_user_profile_logic

class CreateNPSView(APIView):
    def get(self, request, user_id, week_monday, week_sunday):
        try:
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(User=user)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found."}, status=status.HTTP_404_NOT_FOUND)

        if NP.objects.filter(
                UserProfile=user_profile,
                user_energy_intake=user_profile.Energy_Intake,
                start_date=week_monday,
                end_date=week_sunday,
                #week=1
            ):
            return Response({"error": "User already has weekly plan."}, status=status.HTTP_404_NOT_FOUND)

        result = create_nutrition_plan(user_profile)

        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Save to DB
        user_np = NP.objects.filter(UserProfile=user_profile)
        week = user_np.order_by('-week').first().week + 1 if user_np.exists() else 1

        # Create an NP for this user for this week.
        np = NP.objects.create(
            UserProfile=user_profile,
            user_energy_intake=user_profile.Energy_Intake,
            start_date=week_monday,
            end_date=week_sunday,
            week=week
        )

        # Keep the days of the week into a list.
        days = ["Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"]
        # Keep the meal types into a list.
        meal_types = ["Breakfast", "Morning Snack",
                    "Lunch", "Afternoon Snack", "Dinner"]

        # Iterate through the final weekly meals.
        for i, day in enumerate(days):
            for j, meal_type in enumerate(meal_types):
                npitem = NPItem.objects.create(
                    np=np,
                    meal=Meal.objects.get(id=result["meals"][i][j]),
                    day=day,
                    meal_type=meal_type,
                )

        return Response(result, status=status.HTTP_200_OK)

class UpdateUserProfileView(APIView):
    def put(self, request, user_id):
        # Validate User
        if not User.objects.filter(id=user_id).exists():
            return Response({"error": f"No User found for id: {user_id}"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(id=user_id)

        # Validate UserProfile
        try:
            user_profile = UserProfile.objects.get(User=user)
        except UserProfile.DoesNotExist:
            return Response({"error": f"No UserProfile for User: {user_id}"}, status=status.HTTP_400_BAD_REQUEST)

        pal_dict = {  # Dictionary to get the corresponding pal value.
            "sedentary": 1.4,
            "moderately": 1.6,
            "active": 1.8,
            "very_active": 2.0,
        }

        energy_intake, bmi, bmr, data = update_user_profile_logic(request.data)

        if not all([energy_intake, bmi, bmr, data]):
            return Response({"error": "Failed to calculate profile characteristics"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Update fields
            user_profile.Energy_Intake = energy_intake
            user_profile.Bmi = bmi
            user_profile.Bmr = bmr
            user_profile.Height = float(data["height"])
            user_profile.Weight = float(data["weight"])
            user_profile.Pal = pal_dict[data["PAL"]]
            user_profile.Preferences = data["dietaryPreferences"]
            user_profile.Allergies = data["allergies"]
            user_profile.Selected_Cuisines = data["selectedCuisines"]
            user_profile.Target_Weight = float(data["target_weight"])
            user_profile.Goal = data["goal"]
            user_profile.TargetGoal = data["targetGoal"]

            # Save only these fields
            user_profile.save(update_fields=[
                "Energy_Intake", "Bmi", "Bmr", "Height", "Weight", "Pal",
                "Preferences", "Allergies", "Selected_Cuisines", "Target_Weight",
                "Goal", "TargetGoal"
            ])
            return Response({"message": "User profile and NP successfully updated."}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "User updated failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateCurrentWeekView(APIView):
    def put(self, request, user_id, week_monday, week_sunday):
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

        result = create_nutrition_plan(user_profile)
        import json
        #print(result)
        #print(json.dumps(result, indent=4))

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

        # Save the new generated weekly meal plan.
        try:
            # Create an NP for this user for this week.
            np = NP.objects.get(UserProfile=user_profile, start_date=week_monday, end_date=week_sunday, week=week)
        except NP.DoesNotExist:
            return Response({"error": "NP not found."}, status=status.HTTP_404_NOT_FOUND)

        # Delete the np.
        np.delete()

        # Create a new np with the new generated weekly meal plans
        np = NP.objects.create(
            UserProfile=user_profile,
            user_energy_intake=user_profile.Energy_Intake,
            start_date=week_monday,
            end_date=week_sunday,
            week=week
        )

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
                                                meal=Meal.objects.get(id=result["meals"][i][j]),
                                                day=day,
                                                meal_type=meal_type)
                #print(np.id, npitem.id, day, Meal.objects.get(id=weekly_results[0]["meals"][i][j]), meal_type)

        return Response({"message": "Weekly NPs updated successfully."}, status=status.HTTP_200_OK)

