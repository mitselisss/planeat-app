'''
The scope of this script/django command is to fill in the the database's table 'app_dishes'. For this to be done it takes as input argument the path of the
Dishes.csv file which is located in the same folder as this script.
The script is a django command, this is why it is located inside the management/commands folder of the Django project and to run it we run the following
commands:
uoc -> python manage.py load_dishes_pandas /home/tsolakidis/Desktop/planeat/recommender_v1/backend/app/management/commands/csv/uoc_dishes.csv
essrg -> python manage.py load_dishes_pandas /home/tsolakidis/Desktop/planeat/recommender_v1/backend/app/management/commands/csv/essrg_dishes.csv
ucd -> python manage.py load_dishes_pandas /home/tsolakidis/Desktop/planeat/recommender_v1/backend/app/management/commands/csv/ucd_dishes.csv
which is the path of the Dishes.csv file.
'''

import csv
from django.core.management.base import BaseCommand
from app.models import Dish, Proximate, Inorganic, Vitamin
import pandas as pd
from django.db import transaction

class Command(BaseCommand):
    help = 'Import data from dish CSV files into Dish model'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting loading dishes...')

        ucd_file_path = "/home/tsolakidis/Desktop/planeat/recommender_v1/backend/app/management/commands/csv/ucd_dishes.csv"
        uoc_file_path = "/home/tsolakidis/Desktop/planeat/recommender_v1/backend/app/management/commands/csv/uoc_dishes.csv"
        essrg_file_path = "/home/tsolakidis/Desktop/planeat/recommender_v1/backend/app/management/commands/csv/essrg_dishes.csv"
        
        with transaction.atomic():
            self.load_dishes_ucd(ucd_file_path)
            self.load_dishes_uoc(uoc_file_path)
            self.load_dishes_essrg(essrg_file_path)

        self.stdout.write(self.style.SUCCESS('Loading dishes complete.'))

    def get_food_code(self, index, food_code, counter):
        if pd.notna(food_code):
            try:
                return [Proximate.objects.get(Food_Code=food_code).Food_Code, Proximate.objects.get(Food_Code=food_code).Group]
            except:
                self.stdout.write(self.style.WARNING(f'Dish {index}: Proximate with id {food_code}, for CoFID_{counter} does not exist.'))
            return None

    def sum_nutritions(self, food_codes, quantities, nutrition):
        nutrition_value = 0
        for i, food_code in enumerate(food_codes):
            if len(food_codes) == len(quantities):
                if nutrition in ["Energy", "Protein", "Fat", "Carbohydrate", "Fibre"]:
                    if getattr(Proximate.objects.get(Food_Code=food_code), nutrition) > 0 and quantities[i] > 0:
                        nutrition_value += getattr(Proximate.objects.get(Food_Code=food_code), nutrition) * quantities[i] / 100
                    else:
                        print(food_code, quantities[i], nutrition, getattr(Proximate.objects.get(Food_Code=food_code), nutrition))
                elif nutrition in ["Calcium", "Iron"]:
                    if getattr(Inorganic.objects.get(Food_Code=food_code), nutrition) > 0 and quantities[i] > 0:
                        nutrition_value += getattr(Inorganic.objects.get(Food_Code=food_code), nutrition) * quantities[i] / 100
                elif nutrition in ["Folate"]:
                    if getattr(Vitamin.objects.get(Food_Code=food_code), nutrition) > 0 and quantities[i] > 0:
                        nutrition_value += getattr(Vitamin.objects.get(Food_Code=food_code), nutrition) * quantities[i] / 100
                else:
                    print("out of scope???", food_code, quantities[i], nutrition)
        return nutrition_value

    def sum_unique_food_groups_quantities(self, food_groups, quantities):
        food_groups_quanities_dict = {}

        for i, food_group in enumerate(food_groups):
            if len(food_groups) == len(quantities):
                if food_group in food_groups_quanities_dict:
                    food_groups_quanities_dict[food_group] += quantities[i]
                else:
                    food_groups_quanities_dict[str(food_group)] = quantities[i]
        food_groups_quanities_list = [[key, value] for key, value in food_groups_quanities_dict.items()]
        return food_groups_quanities_list


    def load_dishes_ucd(self, file_path):
        df = pd.read_csv(file_path)

        for index, row in df.iterrows():
            if pd.isna(row["Description"]):
                break
            
            dish_id = int(row["ID"]) + 1000
            dish_data = {
                'Description': row["Description"],
                'Recipe': row["Recipe (optional)"] if pd.notna(row["Recipe (optional)"]) else -3,
                'Ingredients': [],
                'Quantities': [],
                'Food_Groups': [],
                'Unique_Food_Groups_Quantities': [],
                "Total_Energy": 0,
                "Total_Protein": 0,
                "Total_Fat": 0,
                "Total_Carbs": 0,
                "Total_Fibre": 0,
                "Total_Calcium": 0,
                "Total_Iron": 0,
                "Total_Folate": 0,
            }

            for i in range(10):
                if i == 0:
                    if self.get_food_code(dish_id, row["CoFID  ID"], i+1) is not None:
                        dish_data["Ingredients"].append(self.get_food_code(dish_id, row["CoFID  ID"], i+1)[0])
                        dish_data["Food_Groups"].append(self.get_food_code(dish_id, row["CoFID  ID"], i+1)[1])
                    if row["Quant. (g/ml)"] if pd.notna(row["Quant. (g/ml)"]) else -3 != -3:
                        dish_data["Quantities"].append(row["Quant. (g/ml)"])
                else:
                    if self.get_food_code(dish_id, row["CoFID  ID."+str(i)], i) is not None:
                        dish_data["Ingredients"].append(self.get_food_code(dish_id, row["CoFID  ID."+str(i)], i)[0])
                        dish_data["Food_Groups"].append(self.get_food_code(dish_id, row["CoFID  ID."+str(i)], i)[1])
                    if row["Quant. (g/ml)."+str(i)] if pd.notna(row["Quant. (g/ml)."+str(i)]) else -3 != -3:
                        dish_data["Quantities"].append(row["Quant. (g/ml)."+str(i)])
            
            dish_data["Unique_Food_Groups_Quantities"] = self.sum_unique_food_groups_quantities(dish_data["Food_Groups"], dish_data["Quantities"])

            dish_data["Total_Energy"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Energy")
            dish_data["Total_Protein"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Protein")
            dish_data["Total_Fat"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Fat")
            dish_data["Total_Carbs"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Carbohydrate")
            dish_data["Total_Fibre"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Fibre")
            dish_data["Total_Calcium"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Calcium")
            dish_data["Total_Iron"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Iron")
            dish_data["Total_Folate"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Folate")

            if len(dish_data["Ingredients"]) == len(dish_data["Quantities"]):
                Dish.objects.update_or_create(
                    id=dish_id,
                    defaults=dish_data
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created UCD dish with id {dish_id}'))
            else:
                self.stdout.write(self.style.WARNING(f'UCD - Dish with id {dish_id} has unmached number of ingredients with quantities.'))

    def load_dishes_uoc(self, file_path):
        df = pd.read_csv(file_path)

        for index, row in df.iterrows():
            if pd.isna(row["Name"]):
                break

            dish_id = row["Unnamed: 0"] + 2000
            dish_data = {
                'Description': row["Name"],
                'Recipe': row["Recipe [OPTIONAL]"] if pd.notna(row["Recipe [OPTIONAL]"]) else -3,
                'Ingredients': [],
                'Quantities': [],
                'Food_Groups': [],
                'Unique_Food_Groups_Quantities': [],
                "Total_Energy": 0,
                "Total_Protein": 0,
                "Total_Fat": 0,
                "Total_Carbs": 0,
                "Total_Fibre": 0,
                "Total_Calcium": 0,
                "Total_Iron": 0,
                "Total_Folate": 0,
            }

            for i in range(10):
                if i == 0:
                    if self.get_food_code(dish_id, row["CoFID  ID"], i+1) is not None:
                        dish_data["Ingredients"].append(self.get_food_code(dish_id, row["CoFID  ID"], i+1)[0])
                        dish_data["Food_Groups"].append(self.get_food_code(dish_id, row["CoFID  ID"], i+1)[1])
                    if row["Quantity (g/ml)"] if pd.notna(row["Quantity (g/ml)"]) else -3 != -3:
                        dish_data["Quantities"].append(row["Quantity (g/ml)"])
                else:
                    if self.get_food_code(dish_id, row["CoFID  ID."+str(i)], i) is not None:
                        dish_data["Ingredients"].append(self.get_food_code(dish_id, row["CoFID  ID."+str(i)], i)[0])
                        dish_data["Food_Groups"].append(self.get_food_code(dish_id, row["CoFID  ID."+str(i)], i)[1])
                    if row["Quantity (g/ml)."+str(i)] if pd.notna(row["Quantity (g/ml)."+str(i)]) else -3 != -3:
                        dish_data["Quantities"].append(row["Quantity (g/ml)."+str(i)])
            
            dish_data["Unique_Food_Groups_Quantities"] = self.sum_unique_food_groups_quantities(dish_data["Food_Groups"], dish_data["Quantities"])

            dish_data["Total_Energy"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Energy")
            dish_data["Total_Protein"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Protein")
            dish_data["Total_Fat"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Fat")
            dish_data["Total_Carbs"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Carbohydrate")
            dish_data["Total_Fibre"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Fibre")
            dish_data["Total_Calcium"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Calcium")
            dish_data["Total_Iron"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Iron")
            dish_data["Total_Folate"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Folate")
            
            if len(dish_data["Ingredients"]) == len(dish_data["Quantities"]):
                Dish.objects.update_or_create(
                    id=dish_id,
                    defaults=dish_data
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created UOC dish with id {dish_id}'))
            else:
                self.stdout.write(self.style.WARNING(f'UOC - Dish with id {dish_id} has unmached number of ingredients with quantities.'))
        
    def load_dishes_essrg(self, file_path):
        df = pd.read_csv(file_path)

        for index, row in df.iterrows():
            if pd.isna(row["Name"]):
                break

            dish_id = row["ID"] + 3000
            dish_data = {
                'Description': row["Name"],
                'Recipe': row["Recipe [OPTIONAL]"] if pd.notna(row["Recipe [OPTIONAL]"]) else -3,
                'Ingredients': [],
                'Quantities': [],
                'Food_Groups': [],
                'Unique_Food_Groups_Quantities': [],
                "Total_Energy": 0,
                "Total_Protein": 0,
                "Total_Fat": 0,
                "Total_Carbs": 0,
                "Total_Fibre": 0,
                "Total_Calcium": 0,
                "Total_Iron": 0,
                "Total_Folate": 0,
            }

            for i in range(10):
                if i == 0:
                    if self.get_food_code(dish_id, row["CoFID  ID"], i) is not None:
                        dish_data["Ingredients"].append(self.get_food_code(dish_id, row["CoFID  ID"], i)[0])
                        dish_data["Food_Groups"].append(self.get_food_code(dish_id, row["CoFID  ID"], i)[1])
                    if row["Quantity (g/ml)"] if pd.notna(row["Quantity (g/ml)"]) else -3 != -3:
                        dish_data["Quantities"].append(row["Quantity (g/ml)"])
                else:
                    if self.get_food_code(dish_id, row["CoFID  ID."+str(i)], i) is not None:
                        dish_data["Ingredients"].append(self.get_food_code(dish_id, row["CoFID  ID."+str(i)], i)[0])
                        dish_data["Food_Groups"].append(self.get_food_code(dish_id, row["CoFID  ID."+str(i)], i)[1])
                    if row["Quantity (g/ml)."+str(i)] if pd.notna(row["Quantity (g/ml)."+str(i)]) else -3 != -3:
                        dish_data["Quantities"].append(row["Quantity (g/ml)."+str(i)])
            
            dish_data["Unique_Food_Groups_Quantities"] = self.sum_unique_food_groups_quantities(dish_data["Food_Groups"], dish_data["Quantities"])

            dish_data["Total_Energy"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Energy")
            dish_data["Total_Protein"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Protein")
            dish_data["Total_Fat"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Fat")
            dish_data["Total_Carbs"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Carbohydrate")
            dish_data["Total_Fibre"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Fibre")
            dish_data["Total_Calcium"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Calcium")
            dish_data["Total_Iron"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Iron")
            dish_data["Total_Folate"] = self.sum_nutritions(dish_data["Ingredients"], dish_data["Quantities"], "Folate")
            
            if len(dish_data["Ingredients"]) == len(dish_data["Quantities"]):
                Dish.objects.update_or_create(
                    id=dish_id,
                    defaults=dish_data
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created ESSRG dish with id {dish_id}'))
            else:
                self.stdout.write(self.style.WARNING(f'ESSRG - Dish with id {dish_id} has unmached number of ingredients with quantities.'))

