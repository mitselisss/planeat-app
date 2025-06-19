"""app/admin.py"""
from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Proximate)
admin.site.register(UserProfile)
admin.site.register(NP)
admin.site.register(NPItem)
admin.site.register(Dish)
admin.site.register(Meal)
admin.site.register(UserActions)
admin.site.register(UserAchievements)
admin.site.register(UserActionAchievements)
