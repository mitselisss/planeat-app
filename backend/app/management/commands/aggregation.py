'''
Scope of this script/Django command is to aggregate the information that proximates (ingedients) holds to the dish and meal level. That means, a meal
consists of various ingredients. These ingredients possess info such as energy in kcal, grams of protein, grams of vitamins, in which food group
they belong, and more. Therefore, this script retrieves this information from the ingridients of a meal, sum them up and save them into the
corresponding app_meal table via the Meal Django model. The same think is been done for dishes. Every dish consists of several meals where each meal
holds info such as energy, protein, etc. This cript retrievs this information from the meals, sum it up and save it into the app_dishes table via the
Dishes Django model. 
'''

from django.core.management.base import BaseCommand
from app.models import Dish, Meal, Proximate, Inorganic, Vitamin
from django.db import transaction
from django.db.models import F

class Command(BaseCommand):
    help = 'Precompute and store nutritional values for dishes and meals'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting aggregation of dishes and meals...')

        with transaction.atomic():
            '''
            We splitt the process into two parts (two functions). The first function is to aggregate the info from ingredients level to dish
            and the second function is to aggregate the info from dish level into meal. Therefore the row of running this script is first for the dishes
            and then for the meals. Also, for this script to fill in the info properly the app_dishes and app_meals tables must be allready filled
            with data. Check this and if not then run the load_dishes and load_meals commands.
            '''
            #self.aggregate_dishes()
            self.aggregate_meals()

        self.stdout.write(self.style.SUCCESS('Precomputation complete.'))

    def aggregate_dishes(self):
        """Aggregate ingredient-level data to dish-level."""
        self.stdout.write("Aggregating dishes...")

        # Preload related data to reduce queries
        dishes = Dish.objects.all().prefetch_related(
            "CoFID_1", "CoFID_2", "CoFID_3", "CoFID_4", "CoFID_5",
            "CoFID_6", "CoFID_7", "CoFID_8", "CoFID_9", "CoFID_10"
        )

        # Create lookup dictionaries to reduce queries inside loops
        inorganic_map = {i.Food_Code: i for i in Inorganic.objects.all()}
        vitamin_map = {v.Food_Code: v for v in Vitamin.objects.all()}

        food_group_dict = {
            "Meat": ["MA", "MAA", "MAC", "MAE", "MAG", "MAI", "ME", "MEA", "MEC", "MEE", "MG", "MBG", "MI", "MIG", "MR"],
            "Chicken": ["MC", "MCA", "MCC", "MCE", "MCG", "MI", "MCK", "MCM", "MCO"],
            "Plant_protein": ["DB"],
            "Vegetables": ["DF", "DG", "DI", "DR"],
            "Fruit": ["F", "FA", "FC"],
            "Dairy": ["BA", "BAB", "BAE", "BAH", "BAK", "BAN", "BAR", "BC", "BL", "BN", "BNE", "BNH", "BNS"],
            "Nuts_and_seeds": ["G", "GA"],
            "Fish": ["J", "JA", "JC", "JK", "JM", "JR"],
        }

        def sum_food_group(dish, food_code_group):            
            # Reset all food group counts to zero (only once per dish)
            Dish.objects.filter(id=dish.id).update(
                Meat=0, Chicken=0, Plant_protein=0, Vegetables=0, Fruit=0, 
                Dairy=0, Nuts_and_seeds=0, Fish=0
            )

            # Create an update dictionary to track increments
            update_values = {}
            
            """Increment the count for the correct food group."""
            for food_group, group_list in food_group_dict.items():
                if food_code_group in group_list:
                    value = getattr(dish, food_group)
                    setattr(dish, food_group, value+1)
                    dish.save()

        
        # Preload related data to avoid multiple queries inside the loop
        dishes = Dish.objects.all().prefetch_related("CoFID_1", "CoFID_2", "CoFID_3", "CoFID_4", "CoFID_5", 
                                                    "CoFID_6", "CoFID_7", "CoFID_8", "CoFID_9", "CoFID_10")
        inorganic_map = {i.Food_Code: i for i in Inorganic.objects.all()}
        vitamin_map = {v.Food_Code: v for v in Vitamin.objects.all()}

        for dish in dishes:
            # Initialize totals
            totals = {
                "Total_Energy": 0,
                "Total_Protein": 0,
                "Total_Fat": 0,
                "Total_Carbs": 0,
                "Total_Fibre": 0,
                "Total_Calcium": 0,
                "Total_Iron": 0,
                "Total_Folate": 0,
            }

            setattr(dish, "Meat", 0)
            setattr(dish, "Chicken", 0)
            setattr(dish, "Plant_protein", 0)
            setattr(dish, "Vegetables", 0)
            setattr(dish, "Fruit", 0)
            setattr(dish, "Dairy", 0)
            setattr(dish, "Nuts_and_seeds", 0)
            setattr(dish, "Fish", 0)
            dish.save()

            # Process each ingredient (CoFID)
            for i in range(1, 11):  # CoFID_1 to CoFID_10
                cofid = getattr(dish, f"CoFID_{i}")
                quantity = getattr(dish, f"Quantity_{i}")

                if cofid is not None:
                    totals["Total_Energy"] += cofid.Energy * quantity / 100
                    totals["Total_Protein"] += cofid.Protein * quantity / 100
                    totals["Total_Fat"] += cofid.Fat * quantity / 100
                    totals["Total_Carbs"] += cofid.Carbohydrate * quantity / 100
                    totals["Total_Fibre"] += cofid.Fibre * quantity / 100
                    totals["Total_Calcium"] += inorganic_map.get(cofid.Food_Code, Inorganic()).Calcium * quantity / 100
                    totals["Total_Iron"] += inorganic_map.get(cofid.Food_Code, Inorganic()).Iron * quantity / 100
                    totals["Total_Folate"] += vitamin_map.get(cofid.Food_Code, Vitamin()).Folate * quantity / 100

                    sum_food_group(dish, cofid.Group)  # Categorize into food groups

            # Bulk update dish totals using Django’s `update()`
            Dish.objects.filter(id=dish.id).update(**totals)

            self.stdout.write(f'Aggregated dish {dish.id}')

    def aggregate_meals(self):
        """
        Aggregate dish-level information into meal-level fields.
        """

        meals = Meal.objects.filter().only(
            "Food_Groups", 'Food_Groups_Counter'
        )  # Optimize DB queries
        
        for meal in meals:
            meal_data = {
                "Meat": 0,
                "Plant_protein": 0,
                "Vegetables": 0,
                "Fruit": 0,
                "Dairy": 0,
                "Nuts_and_seeds": 0,
                "Fish": 0,
                
                "prm_q": 0,
                "prm_s": 0,
                "mea_q": 0,
                "mea_s": 0,
                "veg_q": 0,
                "veg_s": 0,
                "fru_q": 0,
                "fru_s": 0,
                "jui_q": 0,
                "jui_s": 0,
                "dai_q": 0,
                "dai_s": 0,
                "che_q": 0,
                "che_s": 0,
                "leg_q": 0,
                "leg_s": 0,
                "nns_q": 0,
                "nns_s": 0,
                "fis_q": 0,
                "fis_s": 0,
                "oif_q": 0,
                "oif_s": 0,
            }

            for groups in meal.Food_Groups:
                for group in groups:
                    if group in ["MA", "MAA", "MAC", "MAE", "MAG", "MAI", "MC", "MCA", "MCC", "MCE", "MCG", "MI", 
                        "MCK", "MCM", "MCO", "ME", "MEA", "MEC", "MEE", "MG", "MBG", "MR"]:
                        meal_data["Meat"] += 1
                    if group in ["DF", "DG", "DI", "DR"]:
                        meal_data["Vegetables"] += 1
                    if group in ["F", "FA"]:
                        meal_data["Fruit"] += 1
                    if group in ["DB"]:
                        meal_data["Plant_protein"] += 1
                    if group in ["BA", "BAB", "BAE", "BAH", "BAK", "BAN", "BAR", "BC", "BL", "BN", "BNE", "BNH", "BNS"]:
                        meal_data["Dairy"] += 1
                    if group in ["G", "GA"]:
                        meal_data["Nuts_and_seeds"] += 1
                    if group in ["J", "JA", "JC", "JK", "JM", "JR"]:
                        meal_data["Fish"] += 1

            for dish in meal.Food_Groups_Counter:
                group, count, quantity = dish
                if group in ["MI", "MIG"]:
                    meal_data["prm_q"] += quantity
                    meal_data["prm_s"] += count
                if group in ["MA", "MAA", "MAC", "MAE", "MAG", "MAI", "MC", "MCA", "MCC", "MCE", "MCG", "MI", 
                    "MCK", "MCM", "MCO", "ME", "MEA", "MEC", "MEE", "MG", "MBG", "MI", "MIG", "MR"]:
                    meal_data["mea_q"] += quantity
                    meal_data["mea_s"] += count
                if group in ["DF", "DG", "DI", "DR"]:
                    meal_data["veg_q"] += quantity
                    meal_data["veg_s"] += count
                if group in ["F", "FA"]:
                    meal_data["fru_q"] += quantity
                    meal_data["fru_s"] += count
                if group in ["FC"]:
                    meal_data["jui_q"] += quantity
                    meal_data["jui_s"] += count
                if group in ["DB"]:
                    meal_data["leg_q"] += quantity
                    meal_data["leg_s"] += count
                if group in ["BA", "BAB", "BAE", "BAH", "BAK", "BAN", "BAR", "BC", "BL", "BN", "BNE", "BNH", "BNS"]:
                    meal_data["dai_q"] += quantity
                    meal_data["dai_s"] += count
                if group in ["BL"]:
                    meal_data["che_q"] += quantity
                    meal_data["che_s"] += count
                if group in ["G", "GA"]:
                    meal_data["nns_q"] += quantity
                    meal_data["nns_s"] += count
                if group in ["J", "JA", "JK", "JM", "JR"]:
                    meal_data["fis_q"] += quantity
                    meal_data["fis_s"] += count
                if group in ["JC"]:
                    meal_data["oif_q"] += quantity
                    meal_data["oif_s"] += count
            
            Meal.objects.update_or_create(
                id=meal.id,
                defaults=meal_data
            )

            self.stdout.write(f'Aggregated meal {meal.id}')