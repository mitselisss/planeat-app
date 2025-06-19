'''Modules for creating Django models'''
from django.db import models
from django.contrib.auth.models import User

class Proximate(models.Model):
    '''asdasdasdas'''
    Food_Code = models.CharField(primary_key=True, max_length=7, default="zero")
    Food_Name = models.CharField(max_length=100)
    Description = models.CharField(max_length=500)
    Group = models.CharField(max_length=3)
    Protein = models.FloatField(max_length=255, blank=True, null=True)
    Fat = models.FloatField(max_length=255, blank=True, null=True)
    Carbohydrate = models.FloatField(max_length=255, blank=True, null=True)
    Energy = models.FloatField(max_length=255, blank=True, null=True)
    Fibre = models.FloatField(max_length=255, blank=True, null=True)


class Vitamin(models.Model):
    '''asdasdasdas'''
    Food_Code = models.CharField(primary_key=True, max_length=7, default="zero")
    Folate = models.FloatField(max_length=255, blank=True, null=True)


class Inorganic(models.Model):
    '''asdasdasdas'''
    Food_Code = models.CharField(primary_key=True, max_length=7, default="zero")
    Calcium = models.FloatField(max_length=255, blank=True, null=True)
    Iron = models.FloatField(max_length=255, blank=True, null=True)


class Dish(models.Model):
    '''asdasdasdas'''
    id = models.IntegerField(primary_key=True)
    Description = models.CharField(max_length=500)
    Recipe = models.CharField(max_length=500)

    Ingredients = models.JSONField(default=list, null=True, blank=True)
    Quantities = models.JSONField(default=list, null=True, blank=True)
    Food_Groups = models.JSONField(default=list, null=True, blank=True)
    Unique_Food_Groups_Quantities = models.JSONField(default=list, null=True, blank=True)

    # Macros
    Total_Energy = models.FloatField(null=True, default=0)
    Total_Protein = models.FloatField(null=True, default=0)
    Total_Fat = models.FloatField(null=True, default=0)
    Total_Carbs = models.FloatField(null=True, default=0)
    Total_Fibre = models.FloatField(null=True, default=0)
    # Micros
    Total_Calcium = models.FloatField(null=True, default=0)
    Total_Iron = models.FloatField(null=True, default=0)
    # Vitamin
    Total_Folate = models.FloatField(null=True, default=0)


class Meal(models.Model):
    id = models.IntegerField(primary_key=True)
    Country = models.CharField(max_length=10, default="Irish")
    Name = models.CharField(max_length=500)
    Description = models.CharField(max_length=500)
    Type = models.CharField(max_length=20)
    Autumn = models.CharField(max_length=1)
    Winter = models.CharField(max_length=1)
    Spring = models.CharField(max_length=1)
    Summer = models.CharField(max_length=1)

    Dishes = models.JSONField(default=list, null=True, blank=True)
    Ingredients = models.JSONField(default=list, null=True, blank=True)
    Quantities = models.JSONField(default=list, null=True, blank=True)
    Food_Groups = models.JSONField(default=list, null=True, blank=True)
    Food_Groups_Counter = models.JSONField(default=list, null=True, blank=True)

    # Nutritions
    Total_Energy = models.FloatField(null=True, default=0)
    Total_Protein = models.FloatField(null=True, default=0)
    Total_Fat = models.FloatField(null=True, default=0)
    Total_Carbs = models.FloatField(null=True, default=0)
    Total_Fibre = models.FloatField(null=True, default=0)
    Total_Calcium = models.FloatField(null=True, default=0)
    Total_Iron = models.FloatField(null=True, default=0)
    Total_Folate = models.FloatField(null=True, default=0)

    # Exceprts Food groups.
    Meat = models.IntegerField(null=True, default=0)
    Plant_protein = models.IntegerField(null=True, default=0)
    Vegetables = models.IntegerField(null=True, default=0)
    Fruit = models.IntegerField(null=True, default=0)
    Dairy = models.IntegerField(null=True, default=0)
    Nuts_and_seeds = models.IntegerField(null=True, default=0)
    Fish = models.IntegerField(null=True, default=0)

    veg_q = models.IntegerField(null=True, default=0)
    veg_s = models.IntegerField(null=True, default=0)
    fru_q = models.IntegerField(null=True, default=0)
    fru_s = models.IntegerField(null=True, default=0)
    jui_q = models.IntegerField(null=True, default=0)
    jui_s = models.IntegerField(null=True, default=0)
    leg_q = models.IntegerField(null=True, default=0)
    leg_s = models.IntegerField(null=True, default=0)
    dai_q = models.IntegerField(null=True, default=0)
    dai_s = models.IntegerField(null=True, default=0)
    che_q = models.IntegerField(null=True, default=0)
    che_s = models.IntegerField(null=True, default=0)
    nns_q = models.IntegerField(null=True, default=0)
    nns_s = models.IntegerField(null=True, default=0)
    blv_s = models.IntegerField(null=True, default=0)

    blv_q = models.IntegerField(null=True, default=0)
    mea_q = models.IntegerField(null=True, default=0)
    mea_s = models.IntegerField(null=True, default=0)
    fis_q = models.IntegerField(null=True, default=0)
    fis_s = models.IntegerField(null=True, default=0)
    oif_q = models.IntegerField(null=True, default=0)
    oif_s = models.IntegerField(null=True, default=0)

    class Meta:
        indexes = [
            models.Index(fields=["Country"]),
            models.Index(fields=["Type"]),
            models.Index(fields=["Winter"]),
            models.Index(fields=["Spring"]),
            models.Index(fields=["Summer"]),
            models.Index(fields=["Autumn"]),
            models.Index(fields=["Meat"]),
            models.Index(fields=["Dairy"]),
            models.Index(fields=["Nuts_and_seeds"]),
            models.Index(fields=["Fish"]),
        ]


class UserProfile(models.Model):
    '''asdasdasdas'''
    User = models.OneToOneField(User, on_delete=models.CASCADE, default=0)
    Role = models.CharField(max_length=10, default="ungender")
    Pilot_Country = models.CharField(max_length=50, null=True, default=None)
    Sex = models.CharField(max_length=10, default="ungender")
    Yob = models.IntegerField(default=1994)
    Age = models.IntegerField(null=True, default=32)
    Height = models.FloatField(default=1.78)
    Weight = models.FloatField(default=75)
    Pal = models.CharField(max_length=50, default="Sedentary")
    Bmi = models.FloatField(default=24.6)
    Bmr = models.FloatField(default=1738)
    Energy_Intake = models.FloatField(default=2000)
    Target_Weight = models.FloatField(default=24.6)
    Goal = models.CharField(max_length=10, default="ungender")
    TargetGoal = models.CharField(max_length=10, default="ungender")
    Allergies = models.CharField(max_length=50, null=True)
    Preferences = models.CharField(max_length=50, null=True)
    Selected_Cuisines = models.JSONField(default=list, null=True, blank=True)
    Main_screen = models.CharField(max_length=10, default="daily")

    def __str__(self):
        return f"UserProfile for User {self.User.username}, {self.User.id}"


class NP(models.Model):
    '''asdasdasdas'''
    UserProfile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    user_energy_intake = models.FloatField(default=2000)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    week = models.IntegerField(null=True)

    def __str__(self):
        return f"NPs for {self.UserProfile} from {self.start_date} to {self.end_date}"


class NPItem(models.Model):
    '''asdasdasdas'''
    np = models.ForeignKey(NP, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    day = models.CharField(max_length=20, default="monday")
    meal_type = models.CharField(max_length=20, default="breakfast")
    valid_day = models.BooleanField(null=True, default=True)
    shopping_list = models.BooleanField(null=True, default=False)
    checked = models.BooleanField(null=True, default=False)

    def __str__(self):
        return f"NPitem {self.meal.id}, {self.np.start_date}, {self.day}, {self.meal_type} for {self.np.UserProfile.User.username}"


class UserActions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"

class UserActionAchievements(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    day = models.CharField(max_length=255, default="")
    action = models.CharField(max_length=255, default="")
    reason = models.CharField(max_length=255, default="", null=True)
    points = models.IntegerField(default=0, null=True) 
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user.username} - action: {self.action} - reason: {self.reason} - points: {self.points}"
    
class UserAchievements(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    badges = models.JSONField(default=list, null=True, blank=True)
    trails = models.JSONField(default=list, null=True, blank=True)
    level = models.IntegerField(default=1)

    def __str__(self):
        return (
        f"{self.user.username} - level: {self.level} - points: {self.points} - "
        f"badges: {len(self.badges)} - trails: {len(self.trails)}"
    )



