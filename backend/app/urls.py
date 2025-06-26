# app/views/n.py
"""Modules for url paths."""
from django.urls import path
from . import views
from .modules.nps import create_nps
from .modules.user_auth import login, register, activate, activation_email, reset_password, reset_password_email
from .modules.create import create_user_profile
from .modules.get import get_daily_np, get_meal_info, get_dishes_info, get_user_weeks, check_weekly_np,\
    get_nutritional_info, get_weekly_food_categories, get_daily_food_categories, get_user_profile,\
    get_weekly_np, get_daily_food_user_goal_categories, get_weekly_food_user_goal_categories
from .modules.update import update_user_profile, update_current_week_nps, update_user_main_screen
from .modules.shopping_list import get_shopping_list, add_to_shopping_list, remove_from_shopping_list, get_shopping_list_ingredients
from .modules.check_eaten import get_check_eaten_list, add_to_check_eaten_list, remove_from_check_eaten_list
from .modules.user_actions import user_action, get_user_achievements, get_user_action_achievements
from .modules.feedback import *

from app.views import *

urlpatterns = [
    path('api/login', login, name="login"),
    path('api/register', register, name="register"),
    path('api/activate/<str:token>', activate, name='activate'),
    path('api/activationEmail/<str:email>', activation_email, name='activationEmail'),
    path('api/resetPassword/<str:token>', reset_password, name='resetPassword'),
    path('api/resetPasswordEmail/<str:email>', reset_password_email, name='resetPasswordEmail'),

    #path('api/create_nps/<int:user_id>/<str:week_monday>/<str:week_sunday>', create_nps, name="create_nps"),
    path('api/create_nps/<int:user_id>/<str:week_monday>/<str:week_sunday>', CreateNPSView.as_view(), name="create_nps"),

    path('api/<str:user_id>/create_profile', create_user_profile, name="create_user_profile"),

    path('api/get_daily_np/<int:user_id>/<str:week_monday>/<str:day>', get_daily_np, name="get_daily_np"),
    path('api/get_meal_info/<int:meal_id>', get_meal_info, name="get_meal_info"),
    path('api/get_dishes_info/<int:meal_id>', get_dishes_info, name="get_dishes_info"),
    path('api/get_user_weeks/<str:user_id>', get_user_weeks, name="get_user_weeks"),
    path('api/check_weekly_np/<int:user_id>/<str:week_monday>/<str:week_sunday>', check_weekly_np, name="check_weekly_np"),
    path('api/get_nutritional_info/<int:user_id>/<str:week_monday>', get_nutritional_info, name='get_nutritional_info'),
    path('api/get_weekly_food_categories/<int:user_id>/<str:week_monday>', get_weekly_food_categories, name='get_weekly_food_categories'),
    path('api/get_daily_food_categories/<int:user_id>/<str:week_monday>/<str:day>', get_daily_food_categories, name='get_daily_food_categories'),
    path('api/get_user_profile/<int:user_id>', get_user_profile, name='get_user_profile'),

    path('api/get_weekly_food_user_goal_categories/<int:user_id>/<str:week_monday>', get_weekly_food_user_goal_categories, name='get_weekly_food_categories'),
    path('api/get_daily_food_user_goal_categories/<int:user_id>/<str:week_monday>/<str:day>', get_daily_food_user_goal_categories, name='get_daily_food_categories'),

    path('api/update_user_profile/<int:user_id>', UpdateUserProfileView.as_view(), name='update_user_profile'),
    path('api/update_user_main_screen/<int:user_id>', update_user_main_screen, name='update_user_main_screen'),
    #path('api/update_current_week_nps/<int:user_id>/<str:week_monday>/<str:week_sunday>', update_current_week_nps, name='update_current_week_nps'),
    path('api/update_current_week_nps/<int:user_id>/<str:week_monday>/<str:week_sunday>', UpdateCurrentWeekView.as_view(), name='update_current_week_nps'),

    path('api/get_shopping_list_ingredients/<int:user_id>/<str:week_monday>', get_shopping_list_ingredients, name="get_shopping_list"),
    path('api/get_shopping_list/<int:user_id>/<str:week_monday>', get_shopping_list, name="get_shopping_list"),
    path('api/add_to_shopping_list/<int:user_id>/<str:week_monday>', add_to_shopping_list, name='add_to_shopping_list'),
    path('api/remove_from_shopping_list/<int:user_id>/<str:week_monday>', remove_from_shopping_list, name='remove_from_shopping_list'),

    path('api/get_check_eaten_list/<int:user_id>/<str:week_monday>', get_check_eaten_list, name="get_check_eaten_list"),
    path('api/add_to_check_eaten_list/<int:user_id>/<str:week_monday>', add_to_check_eaten_list, name='add_to_check_eaten_list'),
    path('api/remove_from_check_eaten_list/<int:user_id>/<str:week_monday>', remove_from_check_eaten_list, name='remove_from_check_eaten_list'),

    path('api/get_weekly_np/<int:user_id>/<str:week_monday>', get_weekly_np, name='get_weekly_np'),

    path('api/user_actions', user_action, name='user_action'),
    path('api/get_user_achievements/<int:user_id>', get_user_achievements, name='get_user_achievements'),
    path('api/get_user_action_achievements/<int:user_id>', get_user_action_achievements, name='get_user_action_achievements'),

    path('api/feedback/<int:user_id>', feedback, name='feedback'),
]
