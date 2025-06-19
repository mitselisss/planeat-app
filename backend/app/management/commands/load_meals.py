'''
The scope of this script/django command is to fill in the the database's table 'app_meals'. For this to be done it takes as input argument the
path of the Meals.csv file which is located in the same folder as this script.
The script is a django command, this is why it is located inside the management/commands folder of the Django project and to run it we run the following
command: python manage.py load_meals /home/tsolakidis/Desktop/planeat/planeat_app/backend/app/management/commands/Meals.csv
which is the path of the Dishes.csv file.
'''

import csv
from django.core.management.base import BaseCommand
from app.models import Meal, Dish
import pandas as pd
from django.db import transaction

class Command(BaseCommand):
    help = 'Import data from CSV file into Dishes model'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting loading meals...')

        ucd_file_path = "/home/tsolakidis/Desktop/planeat/planeat_app/backend/app/management/commands/csv/ucd_meals.csv"
        uoc_file_path = "/home/tsolakidis/Desktop/planeat/planeat_app/backend/app/management/commands/csv/uoc_meals.csv"
        essrg_file_path = "/home/tsolakidis/Desktop/planeat/planeat_app/backend/app/management/commands/csv/essrg_meals.csv"
        
        with transaction.atomic():
            self.load_meals_ucd(ucd_file_path)
            self.load_meals_uoc(uoc_file_path)
            self.load_meals_essrg(essrg_file_path)

        self.stdout.write(self.style.SUCCESS('Loading meals complete.'))
    
    def food_groups_counter(self, food_groups, quantities):
        #print(food_groups)
        #print(quantities)
        #print("------------------------------")
        food_groups_dict = {}
        
        for i, dish in enumerate(food_groups):
            for j, food_group in enumerate(dish):
                if food_group in food_groups_dict and food_groups_dict[str(food_group)][1] == False:
                    food_groups_dict[str(food_group)][0] += 1
                    food_groups_dict[str(food_group)][1] = True
                    food_groups_dict[str(food_group)][2] += quantities[i][j]
                    #print("if", food_groups_dict)
                elif food_group in food_groups_dict and food_groups_dict[str(food_group)][1] == True:
                    #print("conitnue", food_groups_dict)
                    continue
                else:
                    food_groups_dict[str(food_group)] = [1, True, quantities[i][j]]
                    #print("else", food_groups_dict)
            
            for key, value in food_groups_dict.items():
                food_groups_dict[key][1] = False
            #print("initialized", food_groups_dict)
            #print("next round")
        #print("final---")
        #print(food_groups_dict)

        food_groups_list = []
        for key, value in food_groups_dict.items():
            food_groups_list.append([key, food_groups_dict[key][0], food_groups_dict[key][2]])
        #print(food_groups_list)
        #quit()
        return food_groups_list

    def sum_nutritions(self, dishes, nutrition):
        nutrition_value = 0
        for dish in dishes:
            dish = Dish.objects.get(id=dish)
            if getattr(dish, nutrition) > -1:
                nutrition_value += getattr(dish, nutrition)
            else:
                print(dish, nutrition, getattr(dish, nutrition))
                quit()
        return nutrition_value

    def load_meals_ucd(self, file_path):
        df = pd.read_csv(file_path)

        for index, row in df.iterrows():
            if pd.isna(row["Name"]):
                break
            meal_data = {
                "Name": row["Name"],
                "Country": "Ireland",
                "Description": row["Description (optional)"],
                "Type": row["Type"],
                "Autumn": row["Autumn"],
                "Winter": row["Winter"],
                "Spring": row["Spring"],
                "Summer": row["Summer"],
                "Dishes": [],
                "Ingredients": [],
                "Quantities": [],
                "Food_Groups": [],
                "Food_Groups_Counter": [],
                "Total_Energy": 0,
                "Total_Protein": 0,
                "Total_Fat": 0,
                "Total_Carbs": 0,
                "Total_Fibre": 0,
                "Total_Calcium": 0,
                "Total_Iron": 0,
                "Total_Folate": 0,
            }

            def get_dish_id(dish, counter):
                if pd.notna(dish) or dish == "#NAME":
                    dish_id = int(dish) + 1000
                    dish = Dish.objects.get(id=dish_id).id
                    ingredients = Dish.objects.get(id=dish_id).Ingredients
                    quantities = Dish.objects.get(id=dish_id).Quantities
                    food_groups = Dish.objects.get(id=dish_id).Food_Groups
                    try:
                        return [dish, ingredients,quantities, food_groups]
                    except:
                        self.stdout.write(self.style.WARNING(f'Meal {index}: Dish with id {dish_id}, for dish_{counter} does not exist.'))
                    return None

            for i in range(8):
                if get_dish_id(row["Dish #"+str(i+1)], i+1) is not None:
                    meal_data["Dishes"].append(get_dish_id(row["Dish #"+str(i+1)], i+1)[0])
                    meal_data["Ingredients"].append(get_dish_id(row["Dish #"+str(i+1)], i+1)[1])
                    meal_data["Quantities"].append(get_dish_id(row["Dish #"+str(i+1)], i+1)[2])
                    meal_data["Food_Groups"].append(get_dish_id(row["Dish #"+str(i+1)], i+1)[3])

            meal_data["Food_Groups_Counter"] = self.food_groups_counter(meal_data["Food_Groups"], meal_data["Quantities"])
            meal_data["Total_Energy"] = self.sum_nutritions(meal_data["Dishes"], "Total_Energy")
            meal_data["Total_Protein"] = self.sum_nutritions(meal_data["Dishes"], "Total_Protein")
            meal_data["Total_Fat"] = self.sum_nutritions(meal_data["Dishes"], "Total_Fat")
            meal_data["Total_Carbs"] = self.sum_nutritions(meal_data["Dishes"], "Total_Carbs")
            meal_data["Total_Fibre"] = self.sum_nutritions(meal_data["Dishes"], "Total_Fibre")
            meal_data["Total_Calcium"] = self.sum_nutritions(meal_data["Dishes"], "Total_Calcium")
            meal_data["Total_Iron"] = self.sum_nutritions(meal_data["Dishes"], "Total_Iron")
            meal_data["Total_Folate"] = self.sum_nutritions(meal_data["Dishes"], "Total_Folate")
            #print(meal_data)
            Meal.objects.update_or_create(
                id=row["ID"]+1000,
                defaults=meal_data
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created UCD dish with id {row["ID"]+1000}'))

    def load_meals_uoc(self, file_path):
        df = pd.read_csv(file_path)

        for index, row in df.iterrows():
            if pd.isna(row["Name"]):
                break
            
            meal_data = {
                "Name": row["Name"],
                "Country": "Spain",
                "Description": row["Description [OPTIONAL]"],
                "Type": row["Type"],
                "Autumn": row["Autumn"],
                "Winter": row["Winter"],
                "Spring": row["Spring"],
                "Summer": row["Summer"],
                "Dishes": [],
                "Ingredients": [],
                "Quantities": [],
                "Food_Groups": [],
                "Food_Groups_Counter": [],
                "Total_Energy": 0,
                "Total_Protein": 0,
                "Total_Fat": 0,
                "Total_Carbs": 0,
                "Total_Fibre": 0,
                "Total_Calcium": 0,
                "Total_Iron": 0,
                "Total_Folate": 0,
            }

            def get_dish_id(dish, counter):
                if dish == "#NAME?":
                    return None
                elif pd.notna(dish):
                    dish_id = int(dish) + 2000
                    dish = Dish.objects.get(id=dish_id).id
                    ingredients = Dish.objects.get(id=dish_id).Ingredients
                    quantities = Dish.objects.get(id=dish_id).Quantities
                    food_groups = Dish.objects.get(id=dish_id).Food_Groups
                    try:
                        return [dish, ingredients,quantities, food_groups]
                    except:
                        self.stdout.write(self.style.WARNING(f'Meal {index}: Dish with id {dish_id}, for dish_{counter} does not exist.'))
                    return None
                else:
                    return None

            for i in range(8):
                if get_dish_id(row["ID."+str(i+1)], i+1) is not None:
                    meal_data["Dishes"].append(get_dish_id(row["ID."+str(i+1)], i+1)[0])
                    meal_data["Ingredients"].append(get_dish_id(row["ID."+str(i+1)], i+1)[1])
                    meal_data["Quantities"].append(get_dish_id(row["ID."+str(i+1)], i+1)[2])
                    meal_data["Food_Groups"].append(get_dish_id(row["ID."+str(i+1)], i+1)[3])

            meal_data["Food_Groups_Counter"] = self.food_groups_counter(meal_data["Food_Groups"], meal_data["Quantities"])
            meal_data["Total_Energy"] = self.sum_nutritions(meal_data["Dishes"], "Total_Energy")
            meal_data["Total_Protein"] = self.sum_nutritions(meal_data["Dishes"], "Total_Protein")
            meal_data["Total_Fat"] = self.sum_nutritions(meal_data["Dishes"], "Total_Fat")
            meal_data["Total_Carbs"] = self.sum_nutritions(meal_data["Dishes"], "Total_Carbs")
            meal_data["Total_Fibre"] = self.sum_nutritions(meal_data["Dishes"], "Total_Fibre")
            meal_data["Total_Calcium"] = self.sum_nutritions(meal_data["Dishes"], "Total_Calcium")
            meal_data["Total_Iron"] = self.sum_nutritions(meal_data["Dishes"], "Total_Iron")
            meal_data["Total_Folate"] = self.sum_nutritions(meal_data["Dishes"], "Total_Folate")
            Meal.objects.update_or_create(
                id=row["ID"]+2000,
                defaults=meal_data
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created UCD dish with id {int(row["ID"])+2000}'))

    def load_meals_essrg(self, file_path):
        df = pd.read_csv(file_path)

        for index, row in df.iterrows():
            if pd.isna(row["Name"]):
                break
            
            meal_data = {
                "Name": row["Name"],
                "Country": "Hungary",
                "Description": row["Description [OPTIONAL]"],
                "Type": row["Type"],
                "Autumn": row["Autumn"],
                "Winter": row["Winter"],
                "Spring": row["Spring"],
                "Summer": row["Summer"],
                "Dishes": [],
                "Ingredients": [],
                "Quantities": [],
                "Food_Groups": [],
                "Food_Groups_Counter": [],
                "Total_Energy": 0,
                "Total_Protein": 0,
                "Total_Fat": 0,
                "Total_Carbs": 0,
                "Total_Fibre": 0,
                "Total_Calcium": 0,
                "Total_Iron": 0,
                "Total_Folate": 0,
            }

            def get_dish_id(dish, counter):
                if pd.notna(dish):
                    dish_id = int(dish) + 3000
                    if Dish.objects.filter(id=dish_id).exists():
                        dish = Dish.objects.get(id=dish_id).id
                        ingredients = Dish.objects.get(id=dish_id).Ingredients
                        quantities = Dish.objects.get(id=dish_id).Quantities
                        food_groups = Dish.objects.get(id=dish_id).Food_Groups
                        try:
                            return [dish, ingredients,quantities, food_groups]
                        except:
                            self.stdout.write(self.style.WARNING(f'Meal {index}: DIsh with id {dish_id}, for dish_{counter} does not exist.'))
                        return None

            for i in range(8):
                if get_dish_id(row["ID."+str(i+1)], i+1) is not None:
                    meal_data["Dishes"].append(get_dish_id(row["ID."+str(i+1)], i+1)[0])
                    meal_data["Ingredients"].append(get_dish_id(row["ID."+str(i+1)], i+1)[1])
                    meal_data["Quantities"].append(get_dish_id(row["ID."+str(i+1)], i+1)[2])
                    meal_data["Food_Groups"].append(get_dish_id(row["ID."+str(i+1)], i+1)[3])

            meal_data["Food_Groups_Counter"] = self.food_groups_counter(meal_data["Food_Groups"], meal_data["Quantities"])
            meal_data["Total_Energy"] = self.sum_nutritions(meal_data["Dishes"], "Total_Energy")
            meal_data["Total_Protein"] = self.sum_nutritions(meal_data["Dishes"], "Total_Protein")
            meal_data["Total_Fat"] = self.sum_nutritions(meal_data["Dishes"], "Total_Fat")
            meal_data["Total_Carbs"] = self.sum_nutritions(meal_data["Dishes"], "Total_Carbs")
            meal_data["Total_Fibre"] = self.sum_nutritions(meal_data["Dishes"], "Total_Fibre")
            meal_data["Total_Calcium"] = self.sum_nutritions(meal_data["Dishes"], "Total_Calcium")
            meal_data["Total_Iron"] = self.sum_nutritions(meal_data["Dishes"], "Total_Iron")
            meal_data["Total_Folate"] = self.sum_nutritions(meal_data["Dishes"], "Total_Folate")
            Meal.objects.update_or_create(
                id=row["ID"]+3000,
                defaults=meal_data
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created UCD dish with id {int(row["ID"])+3000}'))