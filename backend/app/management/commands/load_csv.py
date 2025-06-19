from django.core.management.base import BaseCommand
import polars as pl
import pandas as pd
import itertools

class Command(BaseCommand):
    help = 'Load the csv and extract statistic insites.'
    
    def handle(self, *args, **kwargs):
        #path = f'/home/tsolakidis/Desktop/planeat/recommender_v1/database_csv/Irish.csv'
        path = f'/home/tsolakidis/Desktop/planeat/recommender_v1/database_csv/Spain.csv'
        #path = f'/home/tsolakidis/Desktop/planeat/recommender_v1/database_csv/Hungary.csv'
        #path = f'/home/tsolakidis/Desktop/planeat/recommender_v1/database_csv/Irish-Spain.csv'
        #path = f'/home/tsolakidis/Desktop/planeat/recommender_v1/database_csv/Irish-Hungary.csv'
        #path = f'/home/tsolakidis/Desktop/planeat/recommender_v1/database_csv/Spain-Hungary.csv'
        #path = f'/home/tsolakidis/Desktop/planeat/recommender_v1/database_csv/Irish-Spain-Hyngary.csv'
        
        chunk_size = 10 ** 9
        min_values = None
        max_values = None
        for chunk in pd.read_csv(path, chunksize=chunk_size):
            numeric_chunk = chunk.select_dtypes(include='number')

            if min_values is None:
                min_values = numeric_chunk.min()
                max_values = numeric_chunk.max()
            else:
                min_values = pd.concat([min_values, numeric_chunk.min()], axis=1).min(axis=1)
                max_values = pd.concat([max_values, numeric_chunk.max()], axis=1).max(axis=1)
        print("Minimum values:\n", min_values)
        print("Maximum values:\n", max_values)
        