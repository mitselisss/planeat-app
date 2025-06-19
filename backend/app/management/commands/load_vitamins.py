'''
This script reads the csv file Vitamins.csv and loads the data to the corresponding tables and attributes.
There are 2 tables/django models: vatiminsinfo and vitaminsvalue. This script read the csv file and:
1) saves the vitamin's info into the vitaminsinfo table/model.
2) saves the vitamin's value into the vitaminsvalue table/model.
To run this script (this commands, because it is a django commands) navigate to the folder where manage.py is located
and run python manage.py load_vitamins
Adjast the file path accordingly if needed.
'''

import csv
from django.core.management.base import BaseCommand
from app.models import Vitamin
from django.db import transaction
import pandas as pd

class Command(BaseCommand):
    help = 'Import data from dish CSV files into Dish model'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting loading vitamins...')

        file_path = "/home/tsolakidis/Desktop/planeat/recommender_v1/backend/app/management/commands/csv/vitamins.csv"
        
        with transaction.atomic():
            self.loader(file_path)

        self.stdout.write(self.style.SUCCESS('Loading vitamins complete.'))

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
                vitamin_data = {
                    "Folate": check_value(row["Folate (µg)"]),
                }

                Vitamin.objects.update_or_create(
                    Food_Code=food_code,
                    defaults=vitamin_data
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created proximate: {food_code}'))
