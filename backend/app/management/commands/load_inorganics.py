'''
The scope of this script/django command is to fill in the the database's table 'app_inorganics'. For this to be done it takes as input argument the path of the
Inorganics.csv file which is located in the same folder as this script.
The script is a django command, this is why it is located inside the management/commands folder of the Django project and to run it we run the following
command: python manage.py load_inorganics /home/tsolakidis/Desktop/planeat/planeat_app/backend/app/management/commands/Inorganics.csv
which is the path of the Dishes.csv file.
'''

import csv
from django.core.management.base import BaseCommand
from app.models import Inorganic
from django.db import transaction
import pandas as pd

class Command(BaseCommand):
    help = 'Import data from dish CSV files into Dish model'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting loading proximates...')

        file_path = "/home/tsolakidis/Desktop/planeat/recommender_v1/backend/app/management/commands/csv/inorganics.csv"
        
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
                inorganic_data = {
                    "Calcium": check_value(row["Calcium (mg)"]),
                    "Iron": check_value(row["Iron (mg)"]),
                }

                Inorganic.objects.update_or_create(
                    Food_Code=food_code,
                    defaults=inorganic_data
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created proximate: {food_code}'))