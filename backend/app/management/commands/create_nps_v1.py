'''
What is this Django command for and how does it work.
This script generates daily meal plans sorted by score attribute.
General idea: we want to make a web app for personalized nutrition which will generate weekly meal plans for each user.
Into a postgres sql database we store the meals into the Meal table. Each meal can be one of the five types (breakfast,
morning snack, lunch, afternoon snack and dinner). A daily meal plan is an instance of these five meals. Here comes this
script. To generate a daily meal plan we first filter the Meal table and save the five meals into corresponding lists.
Then, using the product function of the itertools library we create all possible combinations of the 5 meals.
Having the combinations we iterate each one and calculate the total nutrients like total energy, total protein, etc.
Based on these totals and based on nutritional rules we provide a score for each daily meal plan. Finally, we use
the heapq library to create a heap and store the best daily meal plans based on their score and sort the heap from
grater score to least.

Regading the scoring of a daily meal plan. To do the scoring we check the various nutritions if they are between a range or
if they are greater or less than a number.
'''


from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import Meal
import pandas as pd
from itertools import product
from random import sample, randrange
import heapq

class Command(BaseCommand):
    help = 'Import data from dish CSV files into Dish model'
    def handle(self, *args, **kwargs):
        self.stdout.write('Starting create nps...')
        with transaction.atomic():
            self.create_nps()
        self.stdout.write(self.style.SUCCESS('create nps complete.'))

    def create_nps(self):
        user_weight = 80

        def is_within_range(meal_plan_nutrition, user_nutrition_intake, tolerance, nutrition):
            # Function that checks if the meal_plan_nutrition is between a tolerance.
            lower_bound = user_nutrition_intake * (1 - tolerance)
            upper_bound = user_nutrition_intake * (1 + tolerance)

            percentage_difference = ((meal_plan_nutrition - user_nutrition_intake) / user_nutrition_intake) * 100

            if lower_bound <= meal_plan_nutrition <= upper_bound:
                #print(f"The meal plan {percentage_difference:.3}% is within ±{tolerance}% of the user's {nutrition}.")
                return True

        weight_dict = { # Dictionary that hold the weights for each nutrition
                "kcal_weight": 0.1,
                "protein_weight": 0.08,
                "carb_weight": 0.08,
                "fat_weight": 0.08,
                "fibre_weight": 0.06,
                "calcium_weight": 0.1,
                "iron_weight": 0.1,
                "folate_weight": 0.1,
                "vegetable_q_weight": 0.04,
                "vegetable_s_weight": 0.02,
                "fruit_q_weight": 0.04,
                "fruit_s_weight": 0.2,
                "plant_protein_q_weight": 0.06,
                "dairy_q_weight": 0.02,
                "dairy_s_weight": 0.01,
                "cheese_q_weight": 0.02,
                "cheese_s_weight": 0.01,
                "nuts_and_seeds_q_weight": 0.06,
            }

        # Fetch meals categorized by type
        breakfasts = list(Meal.objects.filter(Type="Breakfast"))
        snacks = list(Meal.objects.filter(Type="Snack"))
        lunches = list(Meal.objects.filter(Type="Lunch"))
        dinners = list(Meal.objects.filter(Type="Dinner"))

        # # One approach is to fech only the 50 first meals.
        # # Reduce dataset size by taking random samples (adjust size as needed)
        # breakfasts_sample = sample(breakfasts, min(50, len(breakfasts)))  # Random 50 Breakfasts
        # snacks_sample = sample(snacks, min(50, len(snacks)))  # Random 50 Snacks
        # lunches_sample = sample(lunches, min(50, len(lunches)))  # Random 50 Lunches
        # dinners_sample = sample(dinners, min(50, len(dinners)))  # Random 50 Dinners

        meal_combinations = product(
            # The five lines below are for the random selection of the meals.
            # breakfasts_sample, 
            # snacks_sample, 
            # lunches_sample, 
            # snacks_sample, # Afternoon snack
            # dinners_sample

            # The five lines below are for feching all the meals from the database.
            # Althought this is not ideal we do it for debuging scopes so we have the
            # same meals every time we run this script and so we can debug it. Later
            # we will use the above 5 lines with the random feching.
            breakfasts, 
            snacks, 
            lunches, 
            snacks, # Afternoon snack
            dinners
        )

        # Process combinations lazily
        def generate_meal_plans():
            for combo in meal_combinations:
                breakfast, morning_snack, lunch, afternoon_snack, dinner = combo

                meal_plan = {
                    "Breakfast": breakfast.id,
                    "Morning Snack": morning_snack.id,
                    "Lunch": lunch.id,
                    "Afternoon Snack": afternoon_snack.id,
                    "Dinner": dinner.id,
                    "Total_Energy": sum([breakfast.Total_Energy, morning_snack.Total_Energy, lunch.Total_Energy, afternoon_snack.Total_Energy, dinner.Total_Energy]),
                    "Total_Protein": sum([breakfast.Total_Protein, morning_snack.Total_Protein, lunch.Total_Protein, afternoon_snack.Total_Protein, dinner.Total_Protein]),
                    "Total_Fat": sum([breakfast.Total_Fat, morning_snack.Total_Fat, lunch.Total_Fat, afternoon_snack.Total_Fat, dinner.Total_Fat]),
                    "Total_Carbs": sum([breakfast.Total_Carbs, morning_snack.Total_Carbs, lunch.Total_Carbs, afternoon_snack.Total_Carbs, dinner.Total_Carbs]),
                    "Total_Fibre": sum([breakfast.Total_Fibre, morning_snack.Total_Fibre, lunch.Total_Fibre, afternoon_snack.Total_Fibre, dinner.Total_Fibre]),
                    "Total_Calcium": sum([breakfast.Total_Calcium, morning_snack.Total_Calcium, lunch.Total_Calcium, afternoon_snack.Total_Calcium, dinner.Total_Calcium]),
                    "Total_Iron": sum([breakfast.Total_Iron, morning_snack.Total_Iron, lunch.Total_Iron, afternoon_snack.Total_Iron, dinner.Total_Iron]),
                    "Total_Folate": sum([breakfast.Total_Folate, morning_snack.Total_Folate, lunch.Total_Folate, afternoon_snack.Total_Folate, dinner.Total_Folate]),
                    "Score": -1,
                    "energy_variable": -1,
                    "protein_variable": -1,
                    "carbohudrate_variable": -1,
                    "fat_variable": -1,
                    "fibre_variable": -1,
                    "calcium_variable": -1,
                    "iron_variable": -1,
                    "folate_variable": -1,
                    "vegetable_quantity_variable": -1,
                    "vegetable_serving_variable": -1,
                    "fruit_quantity_variable": -1,
                    "fruit_serving_variable": -1,
                    "juice_serving_variable": -1,
                    "plant_protein_quantity_variable": -1,
                    "dairy_quantity_variable": -1,
                    "dairy_serving_variable": -1,
                    "cheese_quantity_variable": -1,
                    "cheese_serving_variable": -1,
                    "nuts_and_seeds_quantity_variable": -1,
                    "id": 0,
                }

                yield meal_plan  # Yield instead of returning all at once

        # # This code is randomize the feching. For now we dont use it because we want to debug.
        # # Collect meal plans into a list (this can be adjusted based on how many meal plans you need)
        # meal_plans_list = []
        # meal_plans_generator = generate_meal_plans()
        # number_of_samples = 20000
        # for plan in meal_plans_generator:
        #     meal_plans_list.append(plan)
        #     if len(meal_plans_list) > number_of_samples:  # You can limit the number of plans collected
        #         break

        # # Randomly sample meal plans
        # random_meal_plans = sample(meal_plans_list, min(number_of_samples, len(meal_plans_list)))

        top_meal_plans = []
        N = 20  # Number of top meal plans to keep

        print("id", "  ",
                    "energy", "  ",
                    "protein", "  ",
                    "carb", "      ",
                    "fat", "  ",
                    "fibre", "  ",
                    "calcium", "  ",
                    "iron", "  ",
                    "folate", "  ",
                    "veg_q", "  ",
                    "vege_s", "  ",
                    "fruit_q", "  ",
                    "fruit_s", "  ",
                    "plant", "  ",
                    "dairy_q", " ",
                    "dairy_s", " ",
                    "cheese_q", " ",
                    "cheese_s", " ",
                    "NnS_q", " ",
                    "Score"
            )
        print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

        #for i, daily_meal_plan in enumerate(random_meal_plans):
        for i, daily_meal_plan in enumerate(generate_meal_plans()):
            # The score of this if statement is for not to iterate throug all the combinations and stop after a number of iterations.
            if i == 1000:
                break  # Stop after N iterations

            # Kcal difference
            energy_variable = 0
            user_energy_intake = 2200
            if is_within_range(daily_meal_plan["Total_Energy"], user_energy_intake, 0.05, "Total_Energy"):
                energy_variable = 10
            elif is_within_range(daily_meal_plan["Total_Energy"], user_energy_intake, 0.10, "Total_Energy"):
                energy_variable = 5
            elif is_within_range(daily_meal_plan["Total_Energy"], user_energy_intake, 0.15, "Total_Energy"):
                energy_variable = 0
            else:
                #energy_variable = -1
                continue
            daily_meal_plan["energy_variable"] = energy_variable
            
            # Protein difference
            # Check if the protein that the user needs is between 3 tolerances. If nor then this daily meal is not suitable.
            protein_variable = 0
            user_protein = 0.83*user_weight # g/kg/d
            if is_within_range(daily_meal_plan["Total_Protein"], user_protein, 0.05, "Total_Protein"):
                protein_variable = 10
            elif is_within_range(daily_meal_plan["Total_Protein"], user_protein, 0.10, "Total_Protein"):
                protein_variable = 5
            elif is_within_range(daily_meal_plan["Total_Protein"], user_protein, 0.15, "Total_Protein"):
                protein_variable = 0
            else:
                # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                continue
            daily_meal_plan["protein_variable"] = protein_variable

            # Carbohudrate difference
            # Check if the carbs of the daily meal plan are between 2 tolerances of the user's energy intake.
            carbohudrate_variable = 0
            if 0.45*user_energy_intake/4 <= daily_meal_plan["Total_Carbs"] <= 0.6*user_energy_intake/4:
                carbohudrate_variable = 10
            elif 0.37*user_energy_intake/4 <= daily_meal_plan["Total_Carbs"] <= 0.68*user_energy_intake/4:
                carbohudrate_variable = 0
            else:
                # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                continue
            daily_meal_plan["carbohudrate_variable"] = carbohudrate_variable

            # Fat difference
            # Check if the fats of the daily meal plan are between 2 tolerances of the user's energy intake.
            fat_variable = 0
            if 0.2*user_energy_intake/9 <= daily_meal_plan["Total_Fat"] <= 0.35*user_energy_intake/9:
                fat_variable = 10
            elif 0.16*user_energy_intake/9 <= daily_meal_plan["Total_Fat"] <= 0.39*user_energy_intake/9:
                fat_variable = 0
            else:
                # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                continue
            daily_meal_plan["fat_variable"] = fat_variable

            # Fibre difference
            # The amound that a user needs every day of fibres is fixed at 25 grams. Check how far the grams of fibres of the meal plan are from the fixed value.
            user_fiber_intake = 25
            if user_fiber_intake > 22.5:
                fibre_variable = 10
            elif user_fiber_intake > 20:
                fibre_variable = 5
            elif fibre_variable > 17.5:
                fibre_variable = 0
            else:
                # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                continue
            daily_meal_plan["fibre_variable"] = fibre_variable

            # Calcium difference
            # Check if the calcium of the daily meal plan are between 3 tolerances.
            user_calcium_intake = 1000
            calcium_variable = 0
            if is_within_range(daily_meal_plan["Total_Calcium"], user_calcium_intake, 0.05, "Total_Calcium"):
                calcium_variable = 10
            elif is_within_range(daily_meal_plan["Total_Calcium"], user_calcium_intake, 0.1, "Total_Calcium"):
                calcium_variable = 5
            elif is_within_range(daily_meal_plan["Total_Calcium"], user_calcium_intake, 0.15, "Total_Calcium"):
                calcium_variable = 0
            else:
                # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                continue
            daily_meal_plan["calcium_variable"] = calcium_variable

            # Iron difference
            # Check if the iron of the daily meal plan are between 3 tolerances.
            user_iron_intake = 11
            iron_variable = 0
            if is_within_range(daily_meal_plan["Total_Iron"], user_iron_intake, 0.05, "Total_Iron"):
                iron_variable = 10
            elif is_within_range(daily_meal_plan["Total_Iron"], user_iron_intake, 0.1, "Total_Iron"):
                iron_variable = 5
            elif is_within_range(daily_meal_plan["Total_Iron"], user_iron_intake, 0.15, "Total_Iron"):
                iron_variable = 0
            else:
                # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                continue
            daily_meal_plan["iron_variable"] = iron_variable
            
            # Folate difference
            # Check if the folate of the daily meal plan are between 3 tolerances.
            user_folate_intake = 330
            folate_variable = 0
            if is_within_range(daily_meal_plan["Total_Folate"], user_folate_intake, 0.05, "Total_Folate"):
                folate_variable = 10
            elif is_within_range(daily_meal_plan["Total_Folate"], user_folate_intake, 0.1, "Total_Folate"):
                folate_variable = 5
            elif is_within_range(daily_meal_plan["Total_Folate"], user_folate_intake, 0.15, "Total_Folate"):
                folate_variable = 0
            else:
                # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                continue
            daily_meal_plan["folate_variable"] = folate_variable


            # Here start the code to check the quantity in grams and number of servings for each food group.
            # For each food group we calculate the total grams and serving for the 5 meals.
            breakfast = Meal.objects.get(id=daily_meal_plan["Breakfast"]).Food_Groups_Counter
            morning_snack = Meal.objects.get(id=daily_meal_plan["Morning Snack"]).Food_Groups_Counter
            lunch = Meal.objects.get(id=daily_meal_plan["Lunch"]).Food_Groups_Counter
            afternoon_snack = Meal.objects.get(id=daily_meal_plan["Afternoon Snack"]).Food_Groups_Counter
            dinner = Meal.objects.get(id=daily_meal_plan["Dinner"]).Food_Groups_Counter

            all_types = [breakfast, morning_snack, lunch, afternoon_snack, dinner]

            # Aggregation of food group quantities to daily meal plan level.
            food_group_dict = {} # If a food group is acceptable we save it inot this dictionary alonf side its grams and servings.
            for meal_type in all_types:
                for dish in meal_type:
                    dish_group = dish[0]
                    dish_serving = dish[1]
                    dish_quantity = dish[2]
                    if dish_group in food_group_dict:
                        food_group_dict[str(dish_group)]["serving"] += dish_serving
                        food_group_dict[str(dish_group)]["quantity"] += dish_quantity
                    else:
                        food_group_dict[str(dish_group)] = {
                            "serving": dish_serving,
                            "quantity": dish_quantity,
                        }

            for key, value in food_group_dict.items():
                # Vegetable quantity and serving difference
                vegetable_quantity_variable = 0
                user_vegetable_quantity_intake = 300
                vegetable_serving_variable = 0
                user_vegetable_serving_intake = 3

                if key in ["DF", "DG", "DI", "DR"]:
                    # Vegetable quantity
                    # Check how far the grams of vegetables of the daily meal plan are from the fixed user's needs.
                    if value["quantity"] > 270:
                        vegetable_quantity_variable = 10
                    elif value["quantity"] > 240:
                        vegetable_quantity_variable = 5
                    elif value["quantity"] > 210:
                        vegetable_quantity_variable = 0
                    else:
                        # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                        continue
                    daily_meal_plan["vegetable_quantity_variable"] = vegetable_quantity_variable

                    # Vegetable serving
                    # Check how far the servings of vegetables of the daily meal plan are from the fixed user's needs.
                    if value["serving"] > 2:
                        vegetable_serving_variable = 10
                    elif value["serving"] > 1:
                        vegetable_serving_variable = 5
                    elif value["serving"] > 0:
                        vegetable_serving_variable = 0
                    else:
                        # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                        continue
                    daily_meal_plan["vegetable_serving_variable"] = vegetable_serving_variable

                # Fruits quantity and serving difference
                fruit_quantity_variable = 0
                user_fruit_quantity_intake = 200
                fruit_serving_variable = 0
                user_fruit_serving_intake = 2
                if key in ["F", "FA"]:
                    # Fruits quantity
                    # Check how far the grams of fruits of the daily meal plan are from the fixed user's needs.
                    if is_within_range(value["quantity"], user_fruit_quantity_intake, 0.05, "Fruits quantity"):
                        fruit_quantity_variable = 10
                    elif is_within_range(value["quantity"], user_fruit_quantity_intake, 0.10, "Fruits quantity"):
                        fruit_quantity_variable = 5
                    elif is_within_range(value["quantity"], user_fruit_quantity_intake, 0.15, "Fruits quantity"):
                        fruit_quantity_variable = 0
                    else:
                        # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                        continue
                    daily_meal_plan["fruit_quantity_variable"] = fruit_quantity_variable
                    
                    # Fruits serving
                    # Check how far the servings of fruits of the daily meal plan are from the fixed user's needs.
                    if value["serving"] == user_fruit_serving_intake:
                        fruit_serving_variable = 10
                    elif user_fruit_serving_intake-1 <= value["serving"] <= user_fruit_serving_intake+1:
                        fruit_serving_variable = 0
                    else:
                        # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                        continue
                    daily_meal_plan["fruit_serving_variable"] = fruit_serving_variable

                # Fruit juice serving difference
                # A user must not have more than one juice per day.
                if key in ["FC"]:
                    # Fruits juice serving
                    if value["serving"] > 1:
                        continue
                    daily_meal_plan["juice_serving_variable"] = value["serving"]
                
                # Plant protein quantity difference
                # Check how far the quantity of plant protein of the daily meal plan are from the fixed user's needs.
                plant_protein_quantity_variable = 0
                if key in ["DB"]:
                    if value["quantity"] > 112.5:
                        plant_protein_quantity_variable = 10
                    elif value["quantity"] > 100:
                        plant_protein_quantity_variable = 5
                    elif value["quantity"] > 87.5:
                        plant_protein_quantity_variable = 0
                    else:
                        # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                        continue
                    daily_meal_plan["plant_protein_quantity_variable"] = plant_protein_quantity_variable

                # Dairy quantity, serving, cheese quantoty and cheese serving difference
                dairy_quantity_variable = 0
                dairy_serving_variable = 0
                if key in ["BA", "BC", "BL", "BN"]:
                    # Dairy quantity
                    # Check if the daily meal plan dairy quantity is between limits.
                    if 125 <= value["quantity"] <= 250:
                        dairy_quantity_variable = 10
                    elif 100 <= value["quantity"] <= 275:
                        dairy_quantity_variable = 0
                    else:
                        # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                        continue
                    daily_meal_plan["dairy_quantity_variable"] = dairy_quantity_variable
                    
                    # Dairy serving
                    # Check if the daily meal plan dairy serving is between limits.
                    if 1 <= value["serving"] <= 2:
                        dairy_serving_variable = 10
                    elif 0 <= value["serving"] <= 3:
                        dairy_serving_variable = 0
                    else:
                        # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                        continue
                    daily_meal_plan["dairy_serving_variable"] = dairy_serving_variable

                cheese_quantity_variable = 0
                cheese_serving_variable = 0
                user_cheese_quantity_intake = 25
                user_cheese_serving_intake = 1
                if key in ["BL"]:
                    # Cheese quantity
                    # Check if the daily meal plan cheese quantity in grams is between a tolerance
                    if is_within_range(value["quantity"], user_cheese_quantity_intake, 0.05, "Cheese"):
                        cheese_quantity_variable = 10
                    elif is_within_range(value["quantity"], user_cheese_quantity_intake, 0.1, "Cheese"):
                        cheese_quantity_variable = 5
                    elif is_within_range(value["quantity"], user_cheese_quantity_intake, 0.15, "Cheese"):
                        cheese_quantity_variable = 0
                    else:
                        # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                        continue
                    daily_meal_plan["cheese_quantity_variable"] = cheese_quantity_variable
                    
                    # Cheese serving
                    # Chech if the daily meal plan serving for cheese is between the limits.
                    if value["serving"] == 1:
                        cheese_serving_variable = 10
                    elif user_cheese_serving_intake-1 <= value["serving"] <= user_cheese_serving_intake+1:
                        cheese_serving_variable = 0
                    else:
                        # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                        continue
                    daily_meal_plan["cheese_serving_variable"] = cheese_serving_variable

                # Nuts and seeds quantity difference
                # Check if the grams of the daily meal plan of nuts and seeds are between tolerance.
                nuts_and_seeds_quantity_variable = 0
                user_nuts_and_seeds_quantity_intake = 30
                if key in ["G", "GA"]:
                    if is_within_range(value["quantity"], user_nuts_and_seeds_quantity_intake, 0.05, "Nuts and Seeds"):
                        nuts_and_seeds_quantity_variable = 10
                    elif is_within_range(value["quantity"], user_nuts_and_seeds_quantity_intake, 0.1, "Nuts and Seeds"):
                        nuts_and_seeds_quantity_variable = 5
                    elif is_within_range(value["quantity"], user_nuts_and_seeds_quantity_intake, 0.15, "Nuts and Seeds"):
                        nuts_and_seeds_quantity_variable = 0
                    else:
                        # This else means that the daily meal plan is far from the use's needs and so we dont use it. Go on to the next.
                        continue
                    daily_meal_plan["nuts_and_seeds_quantity_variable"] = value["quantity"]

            # Objective funtion for score
            daily_meal_plan["Score"] = energy_variable * weight_dict["kcal_weight"] + \
                                        protein_variable * weight_dict["protein_weight"] + \
                                        carbohudrate_variable * weight_dict["carb_weight"] + \
                                        fat_variable * weight_dict["fat_weight"] + \
                                        fibre_variable * weight_dict["fibre_weight"] + \
                                        calcium_variable * weight_dict["calcium_weight"] + \
                                        iron_variable * weight_dict["iron_weight"] + \
                                        folate_variable * weight_dict["folate_weight"] + \
                                        vegetable_quantity_variable * weight_dict["vegetable_q_weight"] + \
                                        vegetable_serving_variable * weight_dict["vegetable_s_weight"] + \
                                        fruit_quantity_variable * weight_dict["fruit_q_weight"] + \
                                        fruit_serving_variable * weight_dict["fruit_s_weight"] + \
                                        plant_protein_quantity_variable * weight_dict["plant_protein_q_weight"] + \
                                        dairy_quantity_variable * weight_dict["dairy_q_weight"] + \
                                        dairy_serving_variable * weight_dict["dairy_s_weight"] + \
                                        cheese_quantity_variable * weight_dict["cheese_q_weight"] + \
                                        cheese_serving_variable * weight_dict["cheese_s_weight"] + \
                                        nuts_and_seeds_quantity_variable * weight_dict["nuts_and_seeds_q_weight"]
            
            daily_meal_plan["id"] = i
            # A print function for debugging.
            # print(i, "  ",
            #         energy_variable, weight_dict["kcal_weight"], "  ",
            #         protein_variable, weight_dict["protein_weight"], "  ",
            #         carbohudrate_variable, weight_dict["carb_weight"], "  ",
            #         fat_variable, weight_dict["fat_weight"], "  ",
            #         fibre_variable, weight_dict["fibre_weight"], "  ",
            #         calcium_variable, weight_dict["calcium_weight"], "  ",
            #         iron_variable, weight_dict["iron_weight"], "  ",
            #         folate_variable, weight_dict["folate_weight"], "  ",
            #         vegetable_quantity_variable, weight_dict["vegetable_q_weight"], "  ",
            #         vegetable_serving_variable, weight_dict["vegetable_s_weight"], "  ",
            #         fruit_quantity_variable, weight_dict["fruit_q_weight"], "  ",
            #         fruit_serving_variable, weight_dict["fruit_s_weight"], "  ",
            #         plant_protein_quantity_variable, weight_dict["plant_protein_q_weight"], "  ",
            #         dairy_quantity_variable, weight_dict["dairy_q_weight"], "  ",
            #         dairy_serving_variable, weight_dict["dairy_s_weight"], "  ",
            #         cheese_quantity_variable, weight_dict["cheese_q_weight"], "  ",
            #         cheese_serving_variable, weight_dict["cheese_s_weight"], "  ",
            #         nuts_and_seeds_quantity_variable, weight_dict["nuts_and_seeds_q_weight"], "  ",
            #         round(daily_meal_plan["Score"], 2))

                                        
            # Instead of pushing the whole dictionary, you push just the negative score and the meal plan's ID or index
            heapq.heappush(top_meal_plans, (daily_meal_plan['Score'], i, daily_meal_plan))

            # If we have more than N items, remove the smallest (i.e., the lowest score)
            if len(top_meal_plans) > N:
                heapq.heappop(top_meal_plans)

        print("------------------------------------------------------------------------------------------------------------------------------------------")
        # Now the heap contains the top N meal plans, sorted by score from the grater score to the smaller.
        top_meal_plans.sort(reverse=True, key=lambda x: x[0])

        # Collect all meal plans in a list
        meal_plans_list = []

        # Iterate through top meal plans
        for plan in top_meal_plans:
            meal_plans_list.append({
                "id": plan[2]["id"],
                "Score": plan[2]['Score'],
                "Energy": f"{round(plan[2]['energy_variable'], 2)}",
                "Protein": f"{round(plan[2]['protein_variable'], 2)}",
                "Carbs": f"{round(plan[2]['carbohudrate_variable'], 2)}",
                "Fats": f"{round(plan[2]['fat_variable'], 2)}",
                "Fibre": f"{round(plan[2]['fibre_variable'], 2)}",
                "Calcium": f"{round(plan[2]['calcium_variable'], 2)}",
                "Folate": f"{round(plan[2]['folate_variable'], 2)}",
                "Veg_q": f"{plan[2]['vegetable_quantity_variable']}",
                "Veg_s": f"{plan[2]['vegetable_serving_variable']}",
                "Fru_q": f"{plan[2]['fruit_quantity_variable']}",
                "Fru_s": f"{plan[2]['fruit_serving_variable']}",
                "Jui_s": f"{plan[2]['juice_serving_variable']}",
                "Pla_q": f"{plan[2]['plant_protein_quantity_variable']}",
                "Dai_q": f"{plan[2]['dairy_quantity_variable']}",
                "Dai_s": f"{plan[2]['dairy_serving_variable']}",
                "Che_q": f"{plan[2]['cheese_quantity_variable']}",
                "Che_s": f"{plan[2]['cheese_serving_variable']}",
                "NnS_q": f"{plan[2]['nuts_and_seeds_quantity_variable']}",
            })
        # Convert collected data into a DataFrame
        df = pd.DataFrame(meal_plans_list)

        # Print DataFrame
        print(df)

