'''
This script reads the csv file Proximate.csv and loads the data to the corresponding tables and attributes.
There are 3 tables/django models: Proximate, Proximateinfo and Proximatevalue. This script read the csv file and:
1) saves the food_id, food_name, description, and group on the table Proximate.
2) saves the proximate and the it's additional name on the table Proximateinfo.
3) saves the value of the proximate on the table Proximatevalue.
To run this script (this commands, because it is a django commands) navigate to the folder where manage.py is located
and run: python manage.py load_proximate
Adjast the file path accordingly if needed.
'''

import csv
from django.core.management.base import BaseCommand
from app.models import Proximate
from django.db import transaction
import pandas as pd

class Command(BaseCommand):
    help = 'Import data from dish CSV files into Dish model'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting loading proximates...')

        file_path = "/home/tsolakidis/Desktop/planeat/recommender_v1/backend/app/management/commands/csv/proximates.csv"
        
        with transaction.atomic():
            self.loader(file_path)

        self.stdout.write(self.style.SUCCESS('Loading proximates complete.'))

    def loader(self, file_path):
        df = pd.read_csv(file_path)

        def check_value(nutrition):
            if pd.isna(nutrition) or nutrition == "":  # Check for NaN or empty
                nutrition = -3.0
            elif nutrition == "N":
                nutrition = -2.0
            elif nutrition == "Tr":
                nutrition = -1.0
            else:
                nutrition = float(nutrition)  # Convert valid numerical values to float
            return nutrition

        for index, row in df.iterrows():
            if index > 1:
                food_code = row["Food Code"]
                proximate_data = {
                    "Food_Name": row["Food Name"],
                    "Description": row["Description"],
                    "Group": row["Group"],
                    "Protein": check_value(row["Protein (g)"]),
                    "Fat": check_value(row["Fat (g)"]),
                    "Carbohydrate": check_value(row["Carbohydrate (g)"]),
                    "Energy": check_value(row["Energy (kcal) (kcal)"]),
                    "Fibre": check_value(row["AOAC fibre (g)"]),
                }

                Proximate.objects.update_or_create(
                    Food_Code=food_code,
                    defaults=proximate_data
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created proximate: {food_code}'))
