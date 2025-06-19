from django.core.management.base import BaseCommand
from django.db import transaction, models
from django.db.models import Q
from app.models import Meal
from random import sample
from typing import Dict, List, Tuple, Iterator
from itertools import product
from itertools import combinations
from collections import defaultdict
from datetime import date, timedelta
import pandas as pd
pd.options.display.float_format = '{:.3f}'.format
import random
import numpy as np
np.set_printoptions(suppress=True, formatter={'all': lambda x: f'{x:.6f}'})
import math
from collections import Counter
#import pdb; pdb.set_trace()

def return_best_plan(user_settings):
    daily_gen = DailyMealPlanGenerator(user_settings)
    daily_plans = daily_gen.process()
    if len(daily_plans) == 0:
        print(f'No daily plans found due to nutritional rules, likely jui_s > 1')
        return None, -2
    daily_targets = daily_gen.targets

    weekly_gen = WeeklyMealPlanGenerator(daily_plans, user_settings)
    weekly_plans = weekly_gen.process()
    if len(weekly_plans) == 0:
        print(f'No weekly plans found due to nutritional rules, likely blv_s > 1')
        return None, -3
    weekly_targets = weekly_gen.targets

    best_plan, divercity_depth = Divercity(weekly_plans).process()

    return get_best_meal(user_settings['a/a'], daily_plans, best_plan, daily_targets, weekly_targets, divercity_depth), 0

def get_best_meal(aa, daily_plans, best_plan, daily_targets, weekly_targets, divercity_depth):
    row = {
        'a/a': aa,
        'dd': divercity_depth,
    }

    for i, idx in enumerate(best_plan['idx']):
        dnp = next((d for d in daily_plans if d['idx'] == idx), None)
        for nutrient, value in dnp['nutrition'].items():
            row[f"day_{i+1}_{nutrient}"] = value
        for key, value in daily_targets.items():
            row[f'day_{i+1}_{key}_target'] = value

    for nutrient, value in best_plan['nutrition'].items():
        row[f'week_{nutrient}'] = value
    for key, value in weekly_targets.items():
        row[f'week_{key}_target'] = value
    row[f"score"] = best_plan['score']
    row[f"distance_v1"] = best_plan['distance_v1']
    row[f"distance_v2"] = best_plan['distance_v2']
    row[f"distance_v3"] = best_plan['distance_v3']

    return row

class BaseFunctions:
    def __init__(self, user_settings: Dict, is_daily=False):
        self.user_settings = user_settings
        self.is_daily = is_daily
        self._set_targets()
        self.fields = [
            'Total_Energy',
            'Total_Protein', 'Total_Fat',
            'Total_Carbs',
            'Total_Fibre',
            'Total_Calcium', 'Total_Iron', 'Total_Folate',
            'veg_q', 'veg_s',
            'fru_q', 'fru_s',
            'jui_s',
            'leg_q',
            'dai_q', 'dai_s',
            'che_q', 'che_s',
            'nns_q',
            'mea_q', 'mea_s',
            'blv_q', 'blv_s',
            'fis_q', 'fis_s',
            'oif_q', 'oif_s',
        ]

        cuisine = ""
        for country in user_settings['cuisine']:
            cuisine += country+"_"

        self.country = {
            'Irish_': {
                'Total_Energy_min': 474.56,   'Total_Energy_max': 2876.69,  'Total_Energy_mea': 1527.30,  'Total_Energy_std': 295.48,
                'Total_Protein_min': 15.25,   'Total_Protein_max': 179.51,  'Total_Protein_mea':  80.91,  'Total_Protein_std':  21.97,
                'Total_Fat_min':     5.78,    'Total_Fat_max':    146.54,  'Total_Fat_mea':     48.50,  'Total_Fat_std':     16.89,
                'Total_Carbs_min':  37.98,    'Total_Carbs_max':  479.83,  'Total_Carbs_mea':   205.77,  'Total_Carbs_std':    49.49,
                'Total_Fibre_min':   3.54,    'Total_Fibre_max':   87.01,  'Total_Fibre_mea':    28.69,  'Total_Fibre_std':    10.12,
                'Total_Calcium_min':91.33,    'Total_Calcium_max':2790.62, 'Total_Calcium_mea':  836.53, 'Total_Calcium_std':  339.60,
                'Total_Iron_min':    2.13,    'Total_Iron_max':   46.74,  'Total_Iron_mea':     13.06,  'Total_Iron_std':      4.68,
                'Total_Folate_min': 79.35,    'Total_Folate_max':1054.52, 'Total_Folate_mea':   376.13, 'Total_Folate_std':   124.19,
                'veg_q_min':   0.00,    'veg_q_max':  618.00, 'veg_q_mea':   143.54, 'veg_q_std':     86.39,
                'veg_s_min':   0.00,    'veg_s_max':    8.00, 'veg_s_mea':     2.36, 'veg_s_std':      0.83,
                'fru_q_min':   0.00,    'fru_q_max':  906.00, 'fru_q_mea':   228.46, 'fru_q_std':    131.05,
                'fru_s_min':   0.00,    'fru_s_max':    7.00, 'fru_s_mea':     2.09, 'fru_s_std':      1.05,
                'jui_s_min':   0.00,    'jui_s_max':    3.00, 'jui_s_mea':     0.35, 'jui_s_std':      0.56,
                'leg_q_min':   0.00,    'leg_q_max':  480.00, 'leg_q_mea':    76.28, 'leg_q_std':     84.10,
                'dai_q_min':   0.00,    'dai_q_max': 1125.00, 'dai_q_mea':   265.22, 'dai_q_std':    170.99,
                'dai_s_min':   0.00,    'dai_s_max':    7.00, 'dai_s_mea':     2.16, 'dai_s_std':      1.10,
                'che_q_min':   0.00,    'che_q_max':  244.00, 'che_q_mea':    13.60, 'che_q_std':     27.69,
                'che_s_min':   0.00,    'che_s_max':    4.00, 'che_s_mea':     0.28, 'che_s_std':      0.50,
                'nns_q_min':   0.00,    'nns_q_max':  225.00, 'nns_q_mea':    17.36, 'nns_q_std':     26.35,
                'blv_q_min':   0.00,    'blv_q_max':  200.00, 'blv_q_mea':     8.00, 'blv_q_std':     39.19,
                'blv_s_min':   0.00,    'blv_s_max':    1.00, 'blv_s_mea':     0.04, 'blv_s_std':      0.20,
                'mea_q_min':   0.00,    'mea_q_max':  375.00, 'mea_q_mea':    74.54, 'mea_q_std':     74.91,
                'mea_s_min':   0.00,    'mea_s_max':    3.00, 'mea_s_mea':     0.84, 'mea_s_std':      0.72,
                'fis_q_min':   0.00,    'fis_q_max':  130.00, 'fis_q_mea':    14.00, 'fis_q_std':     38.16,
                'fis_s_min':   0.00,    'fis_s_max':    1.00, 'fis_s_mea':     0.12, 'fis_s_std':      0.32,
                'oif_q_min':   0.00,    'oif_q_max':   65.00, 'oif_q_mea':     8.60, 'oif_q_std':     19.88,
                'oif_s_min':   0.00,    'oif_s_max':    1.00, 'oif_s_mea':     0.16, 'oif_s_std':      0.37,
            },
            'Spain_': {
                'Total_Energy_min': 843.75,  'Total_Energy_max': 4266.11, 'Total_Energy_mea': 2387.32, 'Total_Energy_std': 326.71,
                'Total_Protein_min':16.59,   'Total_Protein_max':267.84,  'Total_Protein_mea':113.20, 'Total_Protein_std': 31.25,
                'Total_Fat_min':    17.02,   'Total_Fat_max':   254.24,  'Total_Fat_mea':   117.76, 'Total_Fat_std':   25.17,
                'Total_Carbs_min':  51.20,   'Total_Carbs_max': 582.43,  'Total_Carbs_mea': 228.55, 'Total_Carbs_std':   54.35,
                'Total_Fibre_min':   0.08,   'Total_Fibre_max':  77.19,  'Total_Fibre_mea':  20.48, 'Total_Fibre_std':    8.46,
                'Total_Calcium_min':145.68,  'Total_Calcium_max':3248.95,'Total_Calcium_mea':1148.29,'Total_Calcium_std': 345.46,
                'Total_Iron_min':    4.06,   'Total_Iron_max':   59.64,  'Total_Iron_mea':   16.42, 'Total_Iron_std':     5.65,
                'Total_Folate_min': 61.98,   'Total_Folate_max':1564.73,'Total_Folate_mea': 435.63,'Total_Folate_std':  169.35,
                'veg_q_min':   0.00,   'veg_q_max':1395.00,'veg_q_mea': 411.85,'veg_q_std':    179.01,
                'veg_s_min':   0.00,   'veg_s_max':  10.00,'veg_s_mea':   3.67,'veg_s_std':      1.17,
                'fru_q_min':   0.00,   'fru_q_max':1680.00,'fru_q_mea': 558.61,'fru_q_std':    216.35,
                'fru_s_min':   0.00,   'fru_s_max':   8.00,'fru_s_mea':   3.79,'fru_s_std':      1.24,
                'jui_s_min':   0.00,   'jui_s_max':   3.00,'jui_s_mea':   0.20,'jui_s_std':      0.43,
                'leg_q_min':   0.00,   'leg_q_max': 350.00,'leg_q_mea':  55.07,'leg_q_std':     77.86,
                'dai_q_min':   0.00,   'dai_q_max':1166.00,'dai_q_mea': 295.33,'dai_q_std':    163.20,
                'dai_s_min':   0.00,   'dai_s_max':   7.00,'dai_s_mea':   2.41,'dai_s_std':      1.19,
                'che_q_min':   0.00,   'che_q_max':375.00,'che_q_mea':  56.40,'che_q_std':     54.77,
                'che_s_min':   0.00,   'che_s_max':   5.00,'che_s_mea':   0.94,'che_s_std':      0.86,
                'nns_q_min':   0.00,   'nns_q_max':162.00,'nns_q_mea':  27.09,'nns_q_std':     23.47,
                'blv_q_min':   0.00,   'blv_q_max': 40.00,'blv_q_mea':   1.03,'blv_q_std':      6.32,
                'blv_s_min':   0.00,   'blv_s_max':  1.00,'blv_s_mea':   0.03,'blv_s_std':      0.16,
                'mea_q_min':   0.00,   'mea_q_max':772.00,'mea_q_mea': 116.97,'mea_q_std':    141.32,
                'mea_s_min':   0.00,   'mea_s_max':   6.00,'mea_s_mea':   0.98,'mea_s_std':      0.97,
                'fis_q_min':   0.00,   'fis_q_max':725.00,'fis_q_mea': 119.58,'fis_q_std':    143.44,
                'fis_s_min':   0.00,   'fis_s_max':   4.00,'fis_s_mea':   0.82,'fis_s_std':      0.91,
                'oif_q_min':   0.00,   'oif_q_max':656.00,'oif_q_mea':  30.92,'oif_q_std':     82.02,
                'oif_s_min':   0.00,   'oif_s_max':   3.00,'oif_s_mea':   0.26,'oif_s_std':      0.48,
            },
            'Hungary_': {
                'Total_Energy_min': 362.13,  'Total_Energy_max': 2997.36, 'Total_Energy_mea': 1628.15, 'Total_Energy_std': 281.03,
                'Total_Protein_min':10.15,   'Total_Protein_max':161.35,  'Total_Protein_mea': 71.00,  'Total_Protein_std': 16.77,
                'Total_Fat_min':     4.39,   'Total_Fat_max':   176.52,  'Total_Fat_mea':    67.15,  'Total_Fat_std':    18.04,
                'Total_Carbs_min':  32.01,   'Total_Carbs_max': 399.96,  'Total_Carbs_mea':  199.55,  'Total_Carbs_std':   43.80,
                'Total_Fibre_min':   0.33,   'Total_Fibre_max':  80.16,  'Total_Fibre_mea':   23.59,  'Total_Fibre_std':    7.73,
                'Total_Calcium_min':61.49,   'Total_Calcium_max':2676.00,'Total_Calcium_mea': 725.67, 'Total_Calcium_std': 247.89,
                'Total_Iron_min':    2.31,   'Total_Iron_max':   44.88,  'Total_Iron_mea':   13.44,  'Total_Iron_std':     4.16,
                'Total_Folate_min': 24.80,   'Total_Folate_max':1284.47,'Total_Folate_mea': 317.82, 'Total_Folate_std':  131.93,
                'veg_q_min':   0.00,   'veg_q_max':1150.00,'veg_q_mea': 261.57,'veg_q_std':    135.47,
                'veg_s_min':   0.00,   'veg_s_max':  14.00,'veg_s_mea':   4.25,'veg_s_std':      1.61,
                'fru_q_min':   0.00,   'fru_q_max': 660.00,'fru_q_mea': 125.00,'fru_q_std':     96.52,
                'fru_s_min':   0.00,   'fru_s_max':   6.00,'fru_s_mea':   1.57,'fru_s_std':      1.00,
                'jui_s_min':   0.00,   'jui_s_max':   1.00,'jui_s_mea':   0.05,'jui_s_std':      0.22,
                'leg_q_min':   0.00,   'leg_q_max': 360.00,'leg_q_mea':  51.64,'leg_q_std':     54.50,
                'dai_q_min':   0.00,   'dai_q_max': 725.00,'dai_q_mea': 139.82,'dai_q_std':    110.07,
                'dai_s_min':   0.00,   'dai_s_max':   7.00,'dai_s_mea':   1.64,'dai_s_std':      1.11,
                'che_q_min':   0.00,   'che_q_max': 405.00,'che_q_mea':  27.55,'che_q_std':     40.94,
                'che_s_min':   0.00,   'che_s_max':   5.00,'che_s_mea':   0.51,'che_s_std':      0.67,
                'nns_q_min':   0.00,   'nns_q_max': 170.00,'nns_q_mea':  21.88,'nns_q_std':     20.36,
                'blv_q_min':   0.00,   'blv_q_max': 350.00,'blv_q_mea':  12.61,'blv_q_std':     27.95,
                'blv_s_min':   0.00,   'blv_s_max':   5.00,'blv_s_mea':   0.25,'blv_s_std':      0.48,
                'mea_q_min':   0.00,   'mea_q_max': 600.00,'mea_q_mea':  67.96,'mea_q_std':     79.51,
                'mea_s_min':   0.00,   'mea_s_max':   7.00,'mea_s_mea':   0.85,'mea_s_std':      0.86,
                'fis_q_min':   0.00,   'fis_q_max': 100.00,'fis_q_mea':   4.50,'fis_q_std':     19.74,
                'fis_s_min':   0.00,   'fis_s_max':   1.00,'fis_s_mea':   0.05,'fis_s_std':      0.22,
                'oif_q_min':   0.00,   'oif_q_max': 320.00,'oif_q_mea':   8.76,'oif_q_std':     27.70,
                'oif_s_min':   0.00,   'oif_s_max':   4.00,'oif_s_mea':   0.14,'oif_s_std':      0.36,
            },
            'Irish_Spain_': {
                'Total_Energy_min': 381.91,  'Total_Energy_max': 4266.11, 'Total_Energy_mea': 2052.94, 'Total_Energy_std': 408.98,
                'Total_Protein_min':  6.23,  'Total_Protein_max': 275.30,  'Total_Protein_mea':100.86,  'Total_Protein_std': 30.55,
                'Total_Fat_min':      4.90,  'Total_Fat_max':   254.24,  'Total_Fat_mea':   90.64,  'Total_Fat_std':    29.60,
                'Total_Carbs_min':   25.29,  'Total_Carbs_max':  603.73,  'Total_Carbs_mea': 219.92,  'Total_Carbs_std':   53.53,
                'Total_Fibre_min':    0.08,  'Total_Fibre_max':   91.25,  'Total_Fibre_mea':  23.87,  'Total_Fibre_std':    9.44,
                'Total_Calcium_min':  74.26, 'Total_Calcium_max':3826.60, 'Total_Calcium_mea':1026.24,'Total_Calcium_std': 356.65,
                'Total_Iron_min':     1.57,  'Total_Iron_max':   65.91,  'Total_Iron_mea':   15.19,  'Total_Iron_std':     5.66,
                'Total_Folate_min':  49.43,  'Total_Folate_max':1701.54, 'Total_Folate_mea':414.61,  'Total_Folate_std':160.05,
                'veg_q_min':    0.00,  'veg_q_max':1395.00, 'veg_q_mea':307.46,  'veg_q_std':   170.86,
                'veg_s_min':    0.00,  'veg_s_max':  10.00, 'veg_s_mea':  3.16,  'veg_s_std':     1.12,
                'fru_q_min':    0.00,  'fru_q_max':1680.00, 'fru_q_mea':428.91,  'fru_q_std':   206.80,
                'fru_s_min':    0.00,  'fru_s_max':  10.00, 'fru_s_mea':  3.14,  'fru_s_std':     1.32,
                'jui_s_min':    0.00,  'jui_s_max':   5.00, 'jui_s_mea':  0.26,  'jui_s_std':     0.49,
                'leg_q_min':    0.00,  'leg_q_max':  480.00, 'leg_q_mea': 63.37,  'leg_q_std':    80.57,
                'dai_q_min':    0.00,  'dai_q_max':1175.00, 'dai_q_mea':283.24,  'dai_q_std':   167.71,
                'dai_s_min':    0.00,  'dai_s_max':   9.00, 'dai_s_mea':  2.31,  'dai_s_std':     1.18,
                'che_q_min':    0.00,  'che_q_max':  375.00, 'che_q_mea':38.80,  'che_q_std':    46.77,
                'che_s_min':    0.00,  'che_s_max':   5.00, 'che_s_mea':  0.67,  'che_s_std':     0.75,
                'nns_q_min':    0.00,  'nns_q_max':  246.00, 'nns_q_mea':23.08,  'nns_q_std':    24.90,
                'blv_q_min':    0.00,  'blv_q_max':  240.00, 'blv_q_mea': 3.66,  'blv_q_std':    24.93,
                'blv_s_min':    0.00,  'blv_s_max':    2.00, 'blv_s_mea': 0.03,  'blv_s_std':     0.17,
                'mea_q_min':    0.00,  'mea_q_max':  772.00, 'mea_q_mea':100.79, 'mea_q_std':   121.92,
                'mea_s_min':    0.00,  'mea_s_max':    6.00, 'mea_s_mea': 0.93,  'mea_s_std':     0.89,
                'fis_q_min':    0.00,  'fis_q_max':  725.00, 'fis_q_mea':79.19,  'fis_q_std':   121.44,
                'fis_s_min':    0.00,  'fis_s_max':    4.00, 'fis_s_mea': 0.55,  'fis_s_std':     0.79,
                'oif_q_min':    0.00,  'oif_q_max':  656.00, 'oif_q_mea':22.15,  'oif_q_std':   66.09,
                'oif_s_min':    0.00,  'oif_s_max':    3.00, 'oif_s_mea': 0.22,  'oif_s_std':     0.44,
            },
            'Irish_Hungary_': {
                'Total_Energy_min': 213.08,  'Total_Energy_max': 3015.20, 'Total_Energy_mea':1586.12, 'Total_Energy_std': 294.42,
                'Total_Protein_min': 4.42,  'Total_Protein_max':195.95,  'Total_Protein_mea':74.61,  'Total_Protein_std': 20.03,
                'Total_Fat_min':     3.13,  'Total_Fat_max':   199.56,  'Total_Fat_mea':59.67,  'Total_Fat_std':    18.37,
                'Total_Carbs_min':  13.99,  'Total_Carbs_max': 479.83,  'Total_Carbs_mea':202.00,  'Total_Carbs_std':   46.83,
                'Total_Fibre_min':   0.33,  'Total_Fibre_max':  93.12,  'Total_Fibre_mea':25.53,  'Total_Fibre_std':     9.00,
                'Total_Calcium_min':52.55,  'Total_Calcium_max':3107.17,'Total_Calcium_mea':770.00,'Total_Calcium_std': 289.87,
                'Total_Iron_min':    0.91,  'Total_Iron_max':   49.91,  'Total_Iron_mea':13.30,  'Total_Iron_std':     4.49,
                'Total_Folate_min': 24.80,  'Total_Folate_max':1567.42, 'Total_Folate_mea':342.18,'Total_Folate_std':  131.87,
                'veg_q_min':   0.00,  'veg_q_max':1157.00, 'veg_q_mea':212.72,'veg_q_std':   122.45,
                'veg_s_min':   0.00,  'veg_s_max':  14.00, 'veg_s_mea': 3.46,  'veg_s_std':     1.43,
                'fru_q_min':   0.00,  'fru_q_max': 934.00, 'fru_q_mea':167.68,'fru_q_std':   114.62,
                'fru_s_min':   0.00,  'fru_s_max':   8.00, 'fru_s_mea': 1.79,  'fru_s_std':     1.03,
                'jui_s_min':   0.00,  'jui_s_max':   3.00, 'jui_s_mea': 0.17,  'jui_s_std':     0.40,
                'leg_q_min':   0.00,  'leg_q_max': 560.00, 'leg_q_mea':60.93, 'leg_q_std':    68.21,
                'dai_q_min':   0.00,  'dai_q_max':1125.00, 'dai_q_mea':192.28,'dai_q_std':   144.63,
                'dai_s_min':   0.00,  'dai_s_max':   9.00, 'dai_s_mea': 1.86,  'dai_s_std':     1.14,
                'che_q_min':   0.00,  'che_q_max': 455.00, 'che_q_mea':21.90, 'che_q_std':    36.44,
                'che_s_min':   0.00,  'che_s_max':   5.00, 'che_s_mea': 0.41,  'che_s_std':     0.61,
                'nns_q_min':   0.00,  'nns_q_max': 240.00, 'nns_q_mea':19.94, 'nns_q_std':    23.02,
                'blv_q_min':   0.00,  'blv_q_max': 450.00, 'blv_q_mea':10.59, 'blv_q_std':    32.75,
                'blv_s_min':   0.00,  'blv_s_max':   5.00, 'blv_s_mea': 0.16,  'blv_s_std':     0.39,
                'mea_q_min':   0.00,  'mea_q_max': 600.00, 'mea_q_mea':70.18,  'mea_q_std':    78.64,
                'mea_s_min':   0.00,  'mea_s_max':   7.00, 'mea_s_mea': 0.84,  'mea_s_std':     0.82,
                'fis_q_min':   0.00,  'fis_q_max': 230.00, 'fis_q_mea': 8.15,  'fis_q_std':    29.17,
                'fis_s_min':   0.00,  'fis_s_max':   2.00, 'fis_s_mea': 0.08,  'fis_s_std':     0.27,
                'oif_q_min':   0.00,  'oif_q_max': 385.00, 'oif_q_mea': 8.49,  'oif_q_std':    25.11,
                'oif_s_min':   0.00,  'oif_s_max':   5.00, 'oif_s_mea': 0.14,  'oif_s_std':     0.37,
            },
            'Spain_Hungary_': {
                'Total_Energy_min': 265.68,  'Total_Energy_max': 4266.11, 'Total_Energy_mea':2007.89, 'Total_Energy_std':396.44,
                'Total_Protein_min': 9.03,  'Total_Protein_max':278.77,  'Total_Protein_mea':92.14,  'Total_Protein_std':30.23,
                'Total_Fat_min':      2.24, 'Total_Fat_max':   254.24,  'Total_Fat_mea':92.46,  'Total_Fat_std':    27.00,
                'Total_Carbs_min':   31.36, 'Total_Carbs_max': 582.43,  'Total_Carbs_mea':214.03, 'Total_Carbs_std':   50.42,
                'Total_Fibre_min':    0.00, 'Total_Fibre_max':   91.07,  'Total_Fibre_mea':22.04,  'Total_Fibre_std':     8.38,
                'Total_Calcium_min': 60.29, 'Total_Calcium_max':3475.15,'Total_Calcium_mea':936.98,'Total_Calcium_std': 323.24,
                'Total_Iron_min':     2.01, 'Total_Iron_max':   65.67,  'Total_Iron_mea':14.93,  'Total_Iron_std':     5.20,
                'Total_Folate_min':  22.15, 'Total_Folate_max':1655.66, 'Total_Folate_mea':376.58,'Total_Folate_std':  157.29,
                'veg_q_min':    0.00, 'veg_q_max':1575.00, 'veg_q_mea':336.49,'veg_q_std':   177.20,
                'veg_s_min':    0.00, 'veg_s_max':  16.00, 'veg_s_mea': 3.96,  'veg_s_std':     1.50,
                'fru_q_min':    0.00, 'fru_q_max':1680.00, 'fru_q_mea':341.98,'fru_q_std':   199.31,
                'fru_s_min':    0.00, 'fru_s_max':   8.00, 'fru_s_mea': 2.68,  'fru_s_std':     1.30,
                'jui_s_min':    0.00, 'jui_s_max':   4.00, 'jui_s_mea': 0.13,  'jui_s_std':     0.35,
                'leg_q_min':    0.00, 'leg_q_max': 460.00, 'leg_q_mea':53.34,  'leg_q_std':    67.31,
                'dai_q_min':    0.00, 'dai_q_max':1166.00, 'dai_q_mea':217.46, 'dai_q_std':   144.86,
                'dai_s_min':    0.00, 'dai_s_max':   7.00, 'dai_s_mea': 2.02,  'dai_s_std':     1.16,
                'che_q_min':    0.00, 'che_q_max': 455.00, 'che_q_mea':42.00,  'che_q_std':    49.15,
                'che_s_min':    0.00, 'che_s_max':   5.00, 'che_s_mea': 0.73,  'che_s_std':     0.78,
                'nns_q_min':    0.00, 'nns_q_max': 186.00, 'nns_q_mea':24.48,  'nns_q_std':    22.36,
                'blv_q_min':    0.00, 'blv_q_max': 350.00, 'blv_q_mea': 6.81,  'blv_q_std':    20.43,
                'blv_s_min':    0.00, 'blv_s_max':   5.00, 'blv_s_mea': 0.14,  'blv_s_std':     0.36,
                'mea_q_min':    0.00, 'mea_q_max': 872.00, 'mea_q_mea':92.55,  'mea_q_std':   116.46,
                'mea_s_min':    0.00, 'mea_s_max':   8.00, 'mea_s_mea': 0.92,  'mea_s_std':     0.93,
                'fis_q_min':    0.00, 'fis_q_max': 725.00, 'fis_q_mea':62.16,  'fis_q_std':   110.51,
                'fis_s_min':    0.00, 'fis_s_max':   4.00, 'fis_s_mea': 0.44,  'fis_s_std':     0.72,
                'oif_q_min':    0.00, 'oif_q_max': 800.00, 'oif_q_mea':19.79,  'oif_q_std':    61.88,
                'oif_s_min':    0.00, 'oif_s_max':   5.00, 'oif_s_mea': 0.20,  'oif_s_std':     0.43,
            },
            'Irish_Spain_Hungary_': {
                'Total_Energy_min': 213.08,  'Total_Energy_max': 4266.11, 'Total_Energy_mea':1890.76, 'Total_Energy_std':396.05,
                'Total_Protein_min': 4.42,  'Total_Protein_max':286.23,  'Total_Protein_mea':89.41,  'Total_Protein_std':28.86,
                'Total_Fat_min':      2.24, 'Total_Fat_max':   254.24,  'Total_Fat_mea':81.68,  'Total_Fat_std':     27.08,
                'Total_Carbs_min':   13.99, 'Total_Carbs_max': 603.73,  'Total_Carbs_mea':212.14, 'Total_Carbs_std':   50.69,
                'Total_Fibre_min':    0.00, 'Total_Fibre_max':   97.36,  'Total_Fibre_mea':23.71,  'Total_Fibre_std':     9.00,
                'Total_Calcium_min': 51.35, 'Total_Calcium_max':3826.60,'Total_Calcium_mea':912.90,'Total_Calcium_std':329.84,
                'Total_Iron_min':     0.91, 'Total_Iron_max':   66.42,  'Total_Iron_mea':14.51,  'Total_Iron_std':     5.23,
                'Total_Folate_min':  22.15, 'Total_Folate_max':1792.47, 'Total_Folate_mea':377.99,'Total_Folate_std':  152.65,
                'veg_q_min':    0.00, 'veg_q_max':1575.00, 'veg_q_mea':288.77,'veg_q_std':   165.59,
                'veg_s_min':    0.00, 'veg_s_max':  16.00, 'veg_s_mea': 3.55,  'veg_s_std':     1.40,
                'fru_q_min':    0.00, 'fru_q_max':1680.00, 'fru_q_mea':314.99,'fru_q_std':   187.88,
                'fru_s_min':    0.00, 'fru_s_max':  10.00, 'fru_s_mea': 2.55,  'fru_s_std':     1.28,
                'jui_s_min':    0.00, 'jui_s_max':   5.00, 'jui_s_mea': 0.18,  'jui_s_std':     0.42,
                'leg_q_min':    0.00, 'leg_q_max': 560.00, 'leg_q_mea':58.79,  'leg_q_std':    72.03,
                'dai_q_min':    0.00, 'dai_q_max':1175.00, 'dai_q_mea':230.32, 'dai_q_std':   153.84,
                'dai_s_min':    0.00, 'dai_s_max':   9.00, 'dai_s_mea': 2.06,  'dai_s_std':     1.17,
                'che_q_min':    0.00, 'che_q_max': 455.00, 'che_q_mea':34.67,  'che_q_std':    45.01,
                'che_s_min':    0.00, 'che_s_max':   5.00, 'che_s_mea': 0.61,  'che_s_std':     0.73,
                'nns_q_min':    0.00, 'nns_q_max': 256.00, 'nns_q_mea':22.60,  'nns_q_std':    23.48,
                'blv_q_min':    0.00, 'blv_q_max': 450.00, 'blv_q_mea': 6.98,  'blv_q_std':    26.17,
                'blv_s_min':    0.00, 'blv_s_max':   5.00, 'blv_s_mea': 0.11,  'blv_s_std':     0.33,
                'mea_q_min':    0.00, 'mea_q_max': 872.00, 'mea_q_mea':88.18,  'mea_q_std':   108.67,
                'mea_s_min':    0.00, 'mea_s_max':   8.00, 'mea_s_mea': 0.90,  'mea_s_std':     0.89,
                'fis_q_min':    0.00, 'fis_q_max': 725.00, 'fis_q_mea':50.76,  'fis_q_std':    99.75,
                'fis_s_min':    0.00, 'fis_s_max':   4.00, 'fis_s_mea': 0.36,  'fis_s_std':     0.66,
                'oif_q_min':    0.00, 'oif_q_max': 800.00, 'oif_q_mea':16.98,  'oif_q_std':    55.03,
                'oif_s_min':    0.00, 'oif_s_max':   5.00, 'oif_s_mea': 0.18,  'oif_s_std':     0.42,
            },
        }
        self.country = self.country[cuisine]

    def _set_targets(self):
        if self.is_daily:
            base = self.user_settings["base_energy"]
            current = self.user_settings["energy_intake"]
            self.targets = {
                'Total_Energy': current,
                'Total_Protein': (current*0.15/4, current*0.25/4),
                'Total_Fat': (current*0.2/9, current*0.35/9),
                'Total_Carbs': (current*0.45/4, current*0.6/4),
                'Total_Fibre': current*25/base,
                'Total_Calcium': current*1000/base,
                'Total_Iron': current*11/base if self.user_settings["sex"] == "Female" else current*17/base,
                'Total_Folate': current*330/base,
                'veg_q': current*300/base,
                'veg_s': 3,
                'fru_q': current*200/base,
                'fru_s': 2,
                'jui_s': 1,
                'leg_q': current*125/base,
                'dai_q': (current*125/base, current*250/base),
                'dai_s': (1, 2),
                'che_q': current*25/base,
                'che_s': 1,
                'nns_q': current*30/base,
            }
            self.NUTRITION_WEIGHTS = {
                'Total_Energy': 0.3,
                'Total_Protein': 0.08,
                'Total_Fat': 0.04,
                'Total_Carbs': 0.04,
                'Total_Fibre': 0.04,
                'Total_Calcium': 0.04,
                'Total_Iron': 0.04,
                'Total_Folate': 0.02,
                'veg_q': 0.06,
                'veg_s': 0.02,
                'fru_q': 0.06,
                'fru_s': 0.02,
                'jui_s': 0,
                'leg_q': 0.1,
                'dai_q': 0.04,
                'dai_s': 0.01,
                'che_q': 0.02,
                'che_s': 0.01,
                'nns_q': 0.06,
            }
            #if sum(value for value in self.NUTRITION_WEIGHTS.values()) != 1:
                #print("daily weights do not sum in 1.0", sum(value for value in self.NUTRITION_WEIGHTS.values()))
        else:
            base = self.user_settings["base_energy"]
            current = self.user_settings["energy_intake"]*7
            self.targets = {
                'Total_Energy': current,
                'Total_Protein': (current*0.15/4, current*0.25/4),
                'Total_Fat': (current*0.2/9, current*0.35/9),
                'Total_Carbs': (current*0.45/4, current*0.6/4),
                'Total_Fibre': current*25/base,
                'Total_Calcium': current*1000/base,
                'Total_Iron': current*11/base if self.user_settings["sex"] == "Female" else current*17/base,
                'Total_Folate': current*330/base,
                'veg_q': current*300/base,
                'veg_s': 3*7,
                'fru_q': current*200/base,
                'fru_s': 2*7,
                'jui_s': 1*7,
                'leg_q': current*125/base,
                'dai_q': (current*125/base, current*250/base),
                'dai_s': (1*7, 2*7),
                'che_q': current*25/base,
                'che_s': 1*7,
                'nns_q': current*30/base,
                'mea_q': current*420/base,
                'mea_s': 3,
                'blv_q': current*140/base,
                'blv_s': 1,
                'fis_q': current*200/base,
                'fis_s': 2,
                'oif_q': current*100/base,
                'oif_s': 1,
            }
            self.NUTRITION_WEIGHTS = {
                'Total_Energy': 0.3,
                'Total_Protein': 0.08,
                'Total_Fat': 0.04,
                'Total_Carbs': 0.04,
                'Total_Fibre': 0.04,
                'Total_Calcium': 0.04,
                'Total_Iron': 0.04,
                'Total_Folate': 0.02,
                'veg_q': 0.04,
                'veg_s': 0.01,
                'fru_q': 0.04,
                'fru_s': 0.01,
                'jui_s': 0,
                'leg_q': 0.1,
                'dai_q': 0.02,
                'dai_s': 0.01,
                'che_q': 0.01,
                'che_s': 0.01,
                'nns_q': 0.05,
                'mea_q': 0.02,
                'mea_s': 0.01,
                'blv_q': 0.01,
                'blv_s': 0.01,
                'fis_q': 0.02,
                'fis_s': 0.01,
                'oif_q': 0.01,
                'oif_s': 0.01,
            }
            #if sum(value for value in self.NUTRITION_WEIGHTS.values()) != 1:
                #print("weekly weights do not sum in 1.0", sum(value for value in self.NUTRITION_WEIGHTS.values()))

    def _filtering(self):
        '''
        Function that filters the whole meals' database based on:
        seasonality, user's preferences, user's allergies, and
        cuisine county/countries
        '''

        current_month = int(str(date.today()).split('-')[1])  # Get current moth.
        season = (
            "winter" if current_month in [12, 1, 2] else
            "spring" if current_month in [3, 4, 5] else
            "summer" if current_month in [6, 7, 8] else
            "autumn"
        )

        SEASSON_FILTERS = {
            "autumn": Q(Autumn="Y"),
            "winter": Q(Winter="Y"),
            "spring": Q(Spring="Y"),
            "summer": Q(Summer="Y"),
        }

        PREFERENCE_FILTERS = {
            "pescatarian": ~Q(Meat__gt=0),  # Exclude meals where Meat > 0
            "vegetarian": ~Q(Meat__gt=0) & ~Q(Fish__gt=0),  # Exclude Meat and Fish
            "vegan": ~Q(Meat__gt=0) & ~Q(Fish__gt=0) & ~Q(Dairy__gt=0),  # Exclude Meat, Fish, and Dairy
        }


        ALLERGY_FILTERS = {
            "milk_allergy": ~Q(Dairy__gt=0),
            "nuts_allergy": ~Q(Nuts_and_seeds__gt=0),
            "milk_nuts_allergy": ~Q(Dairy__gt=0) & ~Q(Nuts_and_seeds__gt=0)
        }

        query = (
            SEASSON_FILTERS[season] &
            Q(Country__in=self.user_settings['cuisine']) &
            PREFERENCE_FILTERS.get(self.user_settings['preference'], Q()) &  # Default to empty Q if preference not found
            ALLERGY_FILTERS.get(self.user_settings['allergy'], Q())  # Default to empty Q if allergy not found
        )

        return Meal.objects.filter(query)

    def _get_five_meals(self, meals):
        """Functions that returns the five meals"""
        meals = [
            meals.filter(Type="Breakfast"),
            meals.filter(Type="Snack"),
            meals.filter(Type="Lunch"),
            meals.filter(Type="Snack"),
            meals.filter(Type="Dinner")
        ]
        return meals

    def _distance(self, prediction: float, target: float) -> float:
        return abs(prediction - target)/target if target != 0 else 0

    def calculate_score(self, nutrition):
        score = 0.0
        score_list = []

        for nutrient, weight in self.NUTRITION_WEIGHTS.items():
            target = self.targets.get(nutrient, 0)
            pred = nutrition.get(nutrient, 0)

            if isinstance(target, tuple): # Range target
                if pred < target[0]:
                    score += weight * self._distance(pred, target[0])
                    score_list.append(self._distance(pred, target[0]))
                elif pred > target[1]:
                    score += weight * self._distance(pred, target[1])
                    score_list.append(self._distance(pred, target[1]))
                else:
                    score += 0
                    score_list.append(0)
            else: # Single value target
                score += weight * self._distance(pred, target)
                score_list.append(self._distance(pred, target))

        return score, score_list

    def min_max_normalize(self, value, min_val, max_val):
        return (value - min_val) / (max_val - min_val)

    def _euclidean_distance_v1(self, predicted, target):
        '''Euclidean distance between target and predicted meal plans without normalization'''

        # Convert values to numpy array
        X_predicted = np.array([v for v in predicted.values() if v is not None])
        X_target = np.array([v for v in target.values() if v is not None])

        # calculating Euclidean distance using linalg.norm()
        return np.linalg.norm(X_target - X_predicted)

    def _euclidean_distance_v2(self, predicted, target):
        '''Euclidean distance between target and predicted meal plans after normalization'''

        predicted_norm = {}
        for key, value in predicted.items():
            predicted_norm[key] = self.min_max_normalize(value, self.country[f'{key}_min'], self.country[f'{key}_max'])
        target_norm = {}
        for key, value in target.items():
            target_norm[key] = self.min_max_normalize(value, self.country[f'{key}_min'], self.country[f'{key}_max'])

        # Convert values to numpy array
        predicted_norm = np.array([v for v in predicted_norm.values() if v is not None])
        target_norm = np.array([v for v in target_norm.values() if v is not None])
        weights = np.array([v for v in self.NUTRITION_WEIGHTS.values() if v is not None])
        distance = np.sqrt(np.sum(weights * (predicted_norm - target_norm) ** 2))
        normalized_distance = distance/(distance + 1.0)

        # calculating and return Euclidean distance using linalg.norm()
        return normalized_distance

    def _euclidean_distance_v3(self, score_list):
        '''Euclidean distance of relative errors from the zero vector multiplied by nutritinal weights'''
        distance = sum(weight * (error**2) for (key, weight), error in zip(self.NUTRITION_WEIGHTS.items(), score_list))
        distance = math.sqrt(distance)
        normalized_distance = distance/(distance + 1.0)
        return normalized_distance

class DailyMealPlanGenerator(BaseFunctions):
    def __init__(self, user_settings):
        super().__init__(user_settings, is_daily=True)
        self.sample_size = 100000

    def generate_combinations(self, meal_groups: List[models.QuerySet]) -> Iterator[Tuple[Meal]]:
        group_counts = [len(g) for g in meal_groups]
        total_combs = np.prod(group_counts)

        if total_combs > self.sample_size:
            return self._random_combination_generator(meal_groups, group_counts)
        else:
            return self._full_combination_generator(meal_groups)

    def _full_combination_generator(self, meal_groups):
        """Lazy generator for all possible combinations"""
        for combo in product(*meal_groups):
            yield combo

    def _random_combination_generator(self, meal_groups, group_counts):
        """Memory-efficient random sampling without pre-generation"""
        for _ in range(self.sample_size):
            yield tuple(
                random.choice(group)
                for group in meal_groups
            )

    def calculate_nutrition(self, meals):
        nutrition_totals = {}
        for field in self.fields:
            nutrition_totals[field] = sum(getattr(m, field) for m in meals)
        return nutrition_totals

    def process(self):
        meals = self._filtering()
        meal_groups = self._get_five_meals(meals)
        top_plans = []

        for idx, combo in enumerate(self.generate_combinations(meal_groups)):
            nutrition = self.calculate_nutrition(combo)
            if nutrition['jui_s'] > 1:
                continue
            score, score_list = self.calculate_score(nutrition)

            target = {}
            pred = {}
            for key, value in self.targets.items():
                if isinstance(self.targets[key], tuple):
                    target[key] = self.targets[key][0] + (self.targets[key][1] - self.targets[key][0])
                    pred[key] = nutrition.get(key, 0)
                else:
                    target[key] = self.targets[key]
                    pred[key] = nutrition.get(key, 0)

            distance_v1 = self._euclidean_distance_v1(pred, target)
            distance_v2 = self._euclidean_distance_v2(pred, target)
            distance_v3 = self._euclidean_distance_v3(score_list)

            top_plans.append({
                "meals": [m.id for m in combo],
                "idx": idx,
                "score": score,
                "distance_v1": distance_v1,
                "distance_v2": distance_v2,
                "distance_v3": distance_v3,
                "nutrition": nutrition,
            })

        filtered_plans = sorted(top_plans, key=lambda x: x['distance_v3'])[:1000]
        random_plans = random.sample(filtered_plans, min(21, len(filtered_plans)))
        final_plans = sorted(random_plans, key=lambda x: x['distance_v3'])
        return final_plans
        #return sorted(top_plans, key=lambda x: x['distance_v3'])[:20]

class WeeklyMealPlanGenerator(BaseFunctions):
    def __init__(self, daily_plans, user_settings):
        super().__init__(user_settings, is_daily=False)
        self.daily_plans = daily_plans

    def calculate_nutrition(self, meals):
        """Aggregate nutritional values and food group totals from meals"""
        return {key: sum(m['nutrition'].get(key, 0) for m in meals) for key in self.NUTRITION_WEIGHTS}

    def _weekly_combinations(self):
        """Generate unique combinations from 21 DNP of 7 days"""
        return combinations(self.daily_plans, 7)

    def process(self) -> List[Dict]:
        top_plans = []

        for idx, combo in enumerate(self._weekly_combinations()):
            nutrition = self.calculate_nutrition(combo)
            if nutrition['blv_s'] > 1:
                continue
            score, score_list = self.calculate_score(nutrition)

            target = {}
            pred = {}
            for key, value in nutrition.items():
                if isinstance(self.targets[key], tuple):
                    target[key] = self.targets[key][1] - self.targets[key][0]
                    pred[key] = nutrition.get(key, 0)
                else:
                    target[key] = self.targets[key]
                    pred[key] = nutrition.get(key, 0)

            distance_v1 = self._euclidean_distance_v1(pred, target)
            distance_v2 = self._euclidean_distance_v2(pred, target)
            distance_v3 = self._euclidean_distance_v3(score_list)

            top_plans.append({
                "meals": [m['meals'] for m in combo],
                "score": score,
                "idx": [m['idx'] for m in combo],
                "distance_v1": distance_v1,
                "distance_v2": distance_v2,
                "distance_v3": distance_v3,
                "nutrition": nutrition,
            })

        return sorted(top_plans, key=lambda x: x['distance_v3'])

class Divercity():
    def __init__(self, weekly_plans):
        self.weekly_plans = weekly_plans
        self.same_dishes = 3
        self.same_meals = 3

    def process(self):
        counter = 0
        for idx, wmp in enumerate(self.weekly_plans):
            meal_frequency = defaultdict(int)
            for day in wmp['meals']:
                for meal in day:
                    meal_frequency[meal] += 1
            if any(value >= self.same_meals for value in meal_frequency.values()):
                #print("diversity error", idx, meal_frequency[max(meal_frequency, key=meal_frequency.get)], meal_frequency[min(meal_frequency, key=meal_frequency.get)])
                counter += 1
                continue
            else:
                #print("diversity ok", idx)
                #self.print_best_week(wmp)
                return wmp, idx

        if counter == len(self.weekly_plans):
            #print("##################################################")
            #print("No divercity found. Just take the best weekly plan")
            #print(self.weekly_plans)
            flat_meals = [item for sublist in self.weekly_plans[0]['meals'] for item in sublist]
            meal_counts = Counter(flat_meals)
            meal_counts_dict = dict(meal_counts)
            #print(meal_counts_dict)
            #print(self.weekly_plans[0])

            #self.print_best_week(self.weekly_plans[0])
            return self.weekly_plans[0], -1

    def print_best_week(self, weekly_plan):
        columns = ['Monday', 'Tusday', 'Wensday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        rows = ['Breakfast', 'Morniing Snack', 'Lunch', 'Afternoon Snack', 'Dinner']
        df = pd.DataFrame(weekly_plan['meals'], columns, rows).transpose()
        print(df)

class Command(BaseCommand):
    help = 'Generate personalized weekly meal plans'

    def handle(self, *args, **kwargs):
        user_settings = self.set_user_profile()

        daily_gen = DailyMealPlanGenerator(user_settings)
        daily_plans = daily_gen.process()
        daily_targets = daily_gen.targets

        weekly_gen = WeeklyMealPlanGenerator(daily_plans, user_settings)
        weekly_plans = weekly_gen.process()
        weekly_targets = weekly_gen.targets

        #self.analyze_results(daily_plans, weekly_plans)
        self.print_results(daily_plans, daily_targets, weekly_plans, weekly_targets, daily_gen.NUTRITION_WEIGHTS)

        best_plan = Divercity(weekly_plans).process()

    def set_user_profile(self):
        return {
            #'a/a': aa,
            'energy_intake': 3007.676618802675,
            'base_energy': 2500,
            'preference': 'omnivore',
            'allergy': 'milk_allergy',
            'cuisine': [
                #'Irish',
                #'Spain',
                'Hungary',
                ],
            'sex': 'male',
        }

    def analyze_results(self, daily: List, weekly: List):
        # Use pandas DataFrame for analysis
        df_daily = pd.DataFrame([self.plan_to_dict(p) for p in daily])
        df_weekly = pd.DataFrame([self.plan_to_dict(p) for p in weekly])

        print("Daily Plans Analysis:")
        #print(df_daily.describe())
        print(df_daily)
        print("\nWeekly Plans Analysis:")
        #print(df_weekly.describe())
        print(df_weekly)

    def plan_to_dict(self, plan: Tuple) -> Dict:
        # Convert plan tuple to dictionary
        return plan["nutrition"]

    def print_results(self, daily: List, daily_targets, weekly: List, weekly_targets, weights):
        flattened = []
        for entry in daily:
            row = {
                'score': entry['score'],
                'distance_v1': entry['distance_v1'],
                'distance_v2': entry['distance_v2'],
                'distance_v3': entry['distance_v3'],
                }
            row.update(entry['nutrition'])
            flattened.append(row)

        df_daily = pd.DataFrame(flattened)
        print(daily_targets)
        print("Daily Plans Analysis:")
        print(df_daily)

        flattened = []
        for entry in weekly:
            row = {
                'score': entry['score'],
                'distance_v1': entry['distance_v1'],
                'distance_v2': entry['distance_v2'],
                'distance_v3': entry['distance_v3'],
                }
            row.update(entry['nutrition'])
            flattened.append(row)
        df_weekly = pd.DataFrame(flattened)
        print(weekly_targets)
        print("\nWeekly Plans Analysis:")
        print(df_weekly)
