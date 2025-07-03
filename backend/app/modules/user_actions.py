from rest_framework.decorators import api_view
from ..models import UserActions, UserAchievements, UserActionAchievements, NP
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.db.models import F
from django.db.models import Count

@api_view(['POST'])
def user_action(request):
    # print(request.data['user_id'])
    # print(request.data['action'])

    user = User.objects.get(id=request.data['user_id'])
    action=request.data['action']

    messages = []

    # create a record for the users new action
    new_action = UserActions.objects.create(
        user = user,
        action = action,
    )

    action_date = new_action.created_at.date()
    start_date = action_date - timedelta(days=action_date.weekday())
    # print(start_date)
    day = action_date.strftime("%A")
    # print("---->", day)
    # print(action)

    if action == "login":
        messages += login(user, action, start_date, day)
    elif action == "analytics":
        messages += analytics(user, action, start_date, day)
    elif action == "add_eaten_meal":
        messages += add_eaten_meal(user, action, start_date, day)
    elif action == "remove_eaten_meal":
        messages += remove_eaten_meal(user, action, start_date, day)
    elif action == "download_weekly_plan":
        messages += download_weekly_plan(user, action, start_date, day)
    elif action == "download_shopping_list":
        messages += download_shopping_list(user, action, start_date, day)

    trails(user)
    level(user)

    return JsonResponse({
        "message": "Action processed successfully.",
        "feedback": messages
    }, status=200)

def login(user, action, start_date, day):
    messages = []

    # DAILY LOGIN
    if not UserActionAchievements.objects.filter(user=user, day=day, action=action, start_date=start_date, reason="daily_login").exists():
        UserActionAchievements.objects.create(user=user, day=day, action=action, start_date=start_date, reason="daily_login", points=5)
        UserAchievements.objects.filter(user=user).update(points=F('points') + 5)
        messages.append("🎉 You've earned 5 points for today's login!")

    # 3 TIMES PER WEEK
    if not UserActionAchievements.objects.filter(user=user, action=action, start_date=start_date, reason="3_times_login", points=10).exists():
        if UserActionAchievements.objects.filter(user=user, action=action, start_date=start_date, reason="daily_login").count() >= 3:
            UserActionAchievements.objects.create(user=user, day="", action=action, start_date=start_date, reason="3_times_login", points=10)
            UserAchievements.objects.filter(user=user).update(points=F('points') + 10)
            messages.append("🔥 You logged in 3 times this week and earned 10 bonus points!")

    # 7 TIMES PER WEEK
    if not UserActionAchievements.objects.filter(user=user, action=action, start_date=start_date, reason="7_times_login").exists():
        if UserActionAchievements.objects.filter(user=user, action=action, start_date=start_date, reason="daily_login").count() == 7:
            UserActionAchievements.objects.create(user=user, day="", action=action, start_date=start_date, reason="7_times_login", points=20)
            UserAchievements.objects.filter(user=user).update(points=F('points') + 20)
            messages.append("🏅 Perfect week! You earned 20 points for logging in daily!")

    # BADGES
    user_achievements = UserAchievements.objects.get(user=user)
    #user_achievements, created = UserAchievements.objects.get_or_create(user=user)
    count_logins = UserActionAchievements.objects.filter(user=user, action=action, reason="daily_login").count()

    if "login/getting_started" not in user_achievements.badges and count_logins >= 3:
        user_achievements.badges.append("login/getting_started")
        user_achievements.save()
        messages.append("🏆 Badge Unlocked: Getting Started!")

    if "login/habit_builder" not in user_achievements.badges and count_logins >= 10:
        user_achievements.badges.append("login/habit_builder")
        user_achievements.save()
        messages.append("💪 Badge Unlocked: Habit Builder!")

    if "login/committed_streaker" not in user_achievements.badges and count_logins >= 30:
        user_achievements.badges.append("login/committed_streaker")
        user_achievements.save()
        messages.append("🌟 Badge Unlocked: Committed Streaker!")

    return messages

def analytics(user, action, start_date, day):
    messages = []  # Collect messages about new badges earned

    # DAILY ANALYTICS VISIT
    # Check if user has already visited analytics page this day
    check_daily_analytics = UserActionAchievements.objects.filter(
        user=user,
        day=day,
        action=action,
        start_date=start_date,
        reason="daily_analytics"
    )

    # If not, create the record
    if len(check_daily_analytics) == 0:
        UserActionAchievements.objects.create(
            user=user, day=day, action=action, start_date=start_date, reason="daily_analytics"
        )

    user_achievements = UserAchievements.objects.get(user=user)
    count_analytics = UserActionAchievements.objects.filter(
        user=user, action=action, reason="daily_analytics"
    ).count()

    # ANALYTICS BADGE 1
    if "analytics/data_glancer" not in user_achievements.badges and count_analytics >= 3:
        user_achievements.badges.append("analytics/data_glancer")
        user_achievements.save()
        messages.append("Congrats! You earned the badge: Data Glancer 🏅")

    # ANALYTICS BADGE 2
    if "analytics/insight_seeker" not in user_achievements.badges and count_analytics >= 10:
        user_achievements.badges.append("analytics/insight_seeker")
        user_achievements.save()
        messages.append("Awesome! You earned the badge: Insight Seeker 🌟")

    # ANALYTICS BADGE 3
    if "analytics/analytics_master" not in user_achievements.badges and count_analytics >= 30:
        user_achievements.badges.append("analytics/analytics_master")
        user_achievements.save()
        messages.append("Legendary! You earned the badge: Analytics Master 🏆")

    return messages

def add_eaten_meal(user, action, start_date, day):
    messages = []  # Collect messages about new badges

    UserActionAchievements.objects.create(user=user, day=day, action=action, start_date=start_date, reason="check_meal", points=2)
    UserAchievements.objects.filter(user=user).update(points=F('points') + 2)
    messages.append("Awesome! You earned 2 points for eating this meal!")

    count_add_meals_daily = UserActionAchievements.objects.filter(user=user, action=action, start_date=start_date, day=day, reason="check_meal").count()
    count_remove_meals_daily = UserActionAchievements.objects.filter(user=user, action=action, start_date=start_date, day=day, reason="uncheck_meal").count()
    count_meals_daily = count_add_meals_daily - count_remove_meals_daily

    # ALL FIVE MEALS PER DAY
    ckeck_5_meals_daily = UserActionAchievements.objects.filter(
        user=user,
        action=action,
        start_date=start_date,
        day=day,
        reason="check_5_meals",
        points=10
    )

    if len(ckeck_5_meals_daily) == 0 and count_meals_daily >= 5:
        UserActionAchievements.objects.create(user=user, day=day, action=action, start_date=start_date, reason="check_5_meals", points=10)
        UserAchievements.objects.filter(user=user).update(points=F('points') + 10)
        messages.append("Awesome! You earned 10 points for eating all 5 meals today!")

    user_achievements = UserAchievements.objects.get(user=user)
    count_add_meals = UserActionAchievements.objects.filter(user=user, action=action, reason="check_meal").count()
    count_remove_meals = UserActionAchievements.objects.filter(user=user, action="remove_eaten_meal", reason="uncheck_meal").count()
    meals = count_add_meals - count_remove_meals

    # MEAL BADGE 1
    if "meal_suggestions/first_bite" not in user_achievements.badges and meals >= 1:
        user_achievements.badges.append("meal_suggestions/first_bite")
        user_achievements.save()
        messages.append("Congrats! You earned the badge: First Bite 🍽️")

    # MEAL BADGE 2
    if "meal_suggestions/routine_rookie" not in user_achievements.badges and meals >= 30:
        user_achievements.badges.append("meal_suggestions/routine_rookie")
        user_achievements.save()
        messages.append("Great job! You earned the badge: Routine Rookie 🏅")

    # MEAL BADGE 3
    if "meal_suggestions/healthy_habit" not in user_achievements.badges and meals >= 90:
        user_achievements.badges.append("meal_suggestions/healthy_habit")
        user_achievements.save()
        messages.append("Amazing! You earned the badge: Healthy Habit 🌟")

    count_weekly_meals_added = UserActionAchievements.objects.filter(user=user, start_date=start_date, action=action, reason="check_meal").count()
    count_weekly_meals_removed = UserActionAchievements.objects.filter(user=user, start_date=start_date, action="remove_eaten_meal", reason="uncheck_meal").count()
    meals_weekly = count_weekly_meals_added - count_weekly_meals_removed

    # MEAL ADVANCED BADGE 1
    if "meal_suggestions_advanced/week_one_warrior" not in user_achievements.badges and meals_weekly >= 20:
        user_achievements.badges.append("meal_suggestions_advanced/week_one_warrior")
        user_achievements.save()
        messages.append("You're a Week One Warrior! Badge unlocked! 🏆")

    # MEAL ADVANCED BADGE 2
    if "meal_suggestions_advanced/double_week_devotee" not in user_achievements.badges and meals_weekly >= 40:
        user_achievements.badges.append("meal_suggestions_advanced/double_week_devotee")
        user_achievements.save()
        messages.append("Double Week Devotee badge earned! Keep it up! 🔥")

    # MEAL ADVANCED BADGE 3
    if "meal_suggestions_advanced/four_week_champion" not in user_achievements.badges and meals_weekly >= 80:
        user_achievements.badges.append("meal_suggestions_advanced/four_week_champion")
        user_achievements.save()
        messages.append("Four Week Champion! You're unstoppable! 🏅")

    return messages

def remove_eaten_meal(user, action, start_date, day):
    messages = []

    UserActionAchievements.objects.create(user=user, day=day, action=action, start_date=start_date, reason="uncheck_meal", points=-2)
    UserAchievements.objects.filter(user=user).update(points=F('points') - 2)
    messages.append("You lost 2 points for no longer have eaten this meal.")

    count_add_meals_daily = UserActionAchievements.objects.filter(
        user=user, action=action, start_date=start_date, day=day, reason="check_meal"
    ).count()
    count_remove_meals_daily = UserActionAchievements.objects.filter(
        user=user, action=action, start_date=start_date, day=day, reason="uncheck_meal"
    ).count()
    count_meals_daily = count_add_meals_daily - count_remove_meals_daily

    # ALL FIVE MEALS PER DAY
    ckeck_5_meals_daily = UserActionAchievements.objects.filter(
        user=user,
        action="add_eaten_meal",
        start_date=start_date,
        day=day,
        reason="check_5_meals"
    )

    if ckeck_5_meals_daily.exists() and count_meals_daily < 5:
        UserActionAchievements.objects.filter(
            user=user, start_date=start_date, day=day, action="add_eaten_meal", reason="check_5_meals"
        ).delete()
        UserAchievements.objects.filter(user=user).update(points=F('points') - 10)
        messages.append("You lost 10 points for no longer having 5 meals checked today.")

    user_achievements = UserAchievements.objects.get(user=user)
    count_add_meals = UserActionAchievements.objects.filter(user=user, action="add_eaten_meal", reason="check_meal").count()
    count_remove_meals = UserActionAchievements.objects.filter(user=user, action=action, reason="uncheck_meal").count()
    meals = count_add_meals - count_remove_meals

    # MEAL BADGE 1
    if "meal_suggestions/first_bite" in user_achievements.badges and meals < 1:
        user_achievements.badges.remove("meal_suggestions/first_bite")
        user_achievements.save()
        messages.append("Badge removed: First Bite 🍽️")

    # MEAL BADGE 2
    if "meal_suggestions/routine_rookie" in user_achievements.badges and meals < 30:
        user_achievements.badges.remove("meal_suggestions/routine_rookie")
        user_achievements.save()
        messages.append("Badge removed: Routine Rookie 🏅")

    # MEAL BADGE 3
    if "meal_suggestions/healthy_habit" in user_achievements.badges and meals < 90:
        user_achievements.badges.remove("meal_suggestions/healthy_habit")
        user_achievements.save()
        messages.append("Badge removed: Healthy Habit 🌟")

    count_weekly_meals_added = UserActionAchievements.objects.filter(
        user=user, start_date=start_date, action="add_eaten_meal", reason="check_meal"
    ).count()
    count_weekly_meals_removed = UserActionAchievements.objects.filter(
        user=user, start_date=start_date, action=action, reason="uncheck_meal"
    ).count()
    meals_weekly = count_weekly_meals_added - count_weekly_meals_removed

    # MEAL ADVANCED BADGE 1
    if "meal_suggestions_advanced/week_one_warrior" in user_achievements.badges and meals_weekly < 20:
        user_achievements.badges.remove("meal_suggestions_advanced/week_one_warrior")
        user_achievements.save()
        messages.append("Badge removed: Week One Warrior 🏆")

    # MEAL ADVANCED BADGE 2
    if "meal_suggestions_advanced/double_week_devotee" in user_achievements.badges and meals_weekly < 40:
        user_achievements.badges.remove("meal_suggestions_advanced/double_week_devotee")
        user_achievements.save()
        messages.append("Badge removed: Double Week Devotee 🔥")

    # MEAL ADVANCED BADGE 3
    if "meal_suggestions_advanced/four_week_champion" in user_achievements.badges and meals_weekly < 80:
        user_achievements.badges.remove("meal_suggestions_advanced/four_week_champion")
        user_achievements.save()
        messages.append("Badge removed: Four Week Champion 🏅")

    return messages

def download_weekly_plan(user, action, start_date, day):
    messages = []

    # DAILY DOWNLOAD WEEKLY PLAN
    ckeck_daily_weekly_plan = UserActionAchievements.objects.filter(
        user=user,
        day=day,
        action=action,
        start_date=start_date,
        reason="daily_download_weekly_plan"
    )

    if len(ckeck_daily_weekly_plan) == 0:
        UserActionAchievements.objects.create(
            user=user,
            day=day,
            action=action,
            start_date=start_date,
            reason="daily_download_weekly_plan",
            points=10
        )
        UserAchievements.objects.filter(user=user).update(points=F('points') + 10)
        messages.append("You earned 10 points for downloading your weekly plan today!")

    user_achievements = UserAchievements.objects.get(user=user)
    group_downloads_per_week = UserActionAchievements.objects.filter(
        user=user,
        action=action,
        reason="daily_download_weekly_plan"
    ).values('start_date').annotate(download_count=Count('id')).order_by('start_date')

    count_weeks = group_downloads_per_week.count()

    # BADGE 1
    if 'download_weekly_plan/planner_in_progress' not in user_achievements.badges:
        if count_weeks >= 1:
            user_achievements.badges.append('download_weekly_plan/planner_in_progress')
            user_achievements.save()
            messages.append("Congrats! You earned the badge: Planner in Progress 🗓️")

    # BADGE 2
    if 'download_weekly_plan/strategic_eater' not in user_achievements.badges:
        if count_weeks >= 2:
            user_achievements.badges.append('download_weekly_plan/strategic_eater')
            user_achievements.save()
            messages.append("Great job! You earned the badge: Strategic Eater 🍽️")

    # BADGE 3
    if 'download_weekly_plan/plan_mastermind' not in user_achievements.badges:
        if count_weeks >= 4:
            user_achievements.badges.append('download_weekly_plan/plan_mastermind')
            user_achievements.save()
            messages.append("Amazing! You earned the badge: Plan Mastermind 🧠")

    return messages

def download_shopping_list(user, action, start_date, day):
    messages = []

    # DAILY DOWNLOAD SHOPPING LIST
    ckeck_daily_shopping_list = UserActionAchievements.objects.filter(
        user=user,
        day=day,
        action=action,
        start_date=start_date,
        reason="daily_download_shopping_list"
    )

    if len(ckeck_daily_shopping_list) == 0:
        UserActionAchievements.objects.create(
            user=user,
            day=day,
            action=action,
            start_date=start_date,
            reason="daily_download_shopping_list",
            points=5
        )
        UserAchievements.objects.filter(user=user).update(points=F('points') + 5)
        messages.append("You earned 5 points for downloading your shopping list today!")

    user_achievements = UserAchievements.objects.get(user=user)
    count_daily_shopping_list_downloads = UserActionAchievements.objects.filter(
        user=user,
        action=action,
        reason="daily_download_shopping_list"
    ).count()

    # SHOPPING LIST BADGE 1
    if "download_shopping_list/list_soldier" not in user_achievements.badges:
        if count_daily_shopping_list_downloads >= 3:
            user_achievements.badges.append("download_shopping_list/list_soldier")
            user_achievements.save()
            messages.append("Congrats! You earned the badge: List Soldier 🛒")

    # SHOPPING LIST BADGE 2
    if "download_shopping_list/kitchen_commander" not in user_achievements.badges:
        if count_daily_shopping_list_downloads >= 6:
            user_achievements.badges.append("download_shopping_list/kitchen_commander")
            user_achievements.save()
            messages.append("Great job! You earned the badge: Kitchen Commander 🍳")

    # SHOPPING LIST BADGE 3
    if "download_shopping_list/grocery_general" not in user_achievements.badges:
        if count_daily_shopping_list_downloads >= 12:
            user_achievements.badges.append("download_shopping_list/grocery_general")
            user_achievements.save()
            messages.append("Amazing! You earned the badge: Grocery General 🛍️")

    return messages

def level(user):
    user_achievements = UserAchievements.objects.get(user=user)
    points = user_achievements.points
    badges = len(user_achievements.badges)

    new_level = user_achievements.level  # current level
    message = None

    if points >= 1000 and badges >= 18:
        new_level = 5
    elif points >= 600 and badges >= 10:
        new_level = 4
    elif points >= 300 and badges >= 7:
        new_level = 3
    elif points >= 100 and badges >= 3:
        new_level = 2
    else:
        new_level = 1

    if new_level != user_achievements.level:
        user_achievements.level = new_level
        user_achievements.save()
        message = f"Congrats! You've reached level {new_level} 🎉"

    return message

def trails(user):
    user_achievements = UserAchievements.objects.get(user=user)
    badge_set = set(user_achievements.badges)
    current_trails = set(user_achievements.trails)

    trail_map = {
        "planeat_hiker": [
            'login/getting_started',
            'analytics/data_glancer',
            'meal_suggestions/first_bite',
            'meal_suggestions_advanced/week_one_warrior',
            'download_weekly_plan/planner_in_progress',
            'download_shopping_list/list_soldier'
        ],
        "planeat_explorer": [
            'login/habit_builder',
            'analytics/insight_seeker',
            'meal_suggestions/routine_rookie',
            'meal_suggestions_advanced/double_week_devotee',
            'download_weekly_plan/strategic_eater',
            'download_shopping_list/kitchen_commander'
        ],
        "planeat_ranger": [
            'login/committed_streaker',
            'analytics/analytics_master',
            'meal_suggestions/healthy_habit',
            'meal_suggestions_advanced/four_week_champion',
            'download_weekly_plan/plan_mastermind',
            'download_shopping_list/grocery_general'
        ]
    }

    messages = []

    for trail_name, required_badges in trail_map.items():
        if trail_name not in current_trails:
            unlocked_count = sum(1 for badge in required_badges if badge in badge_set)
            if unlocked_count >= 6:
                user_achievements.trails.append(trail_name)
                messages.append(f"Congratulations! You unlocked the trail: {trail_name.replace('_', ' ').title()}")

    if messages:
        user_achievements.save()

    return messages


@api_view(['GET'])
def get_user_achievements(request, user_id):
    user = User.objects.get(id=user_id)
    res = UserAchievements.objects.get(user=user)

    data = {
        'points': res.points,
        'badges': res.badges,
        'trails': res.trails,
        'level': res.level,
    }
    # print(data)

    return Response(data)

@api_view(['GET'])
def get_user_action_achievements(request, user_id):
    user = User.objects.get(id=user_id)
    action_achievements = UserActionAchievements.objects.filter(user=user).exclude(points=0).order_by('-created_at')[:8]

    # for ac in action_achievements:
    #     print(ac.created_at)

    data = [
        {
            "action": ach.action,
            "reason": ach.reason,
            "points": ach.points,
            "date": ach.created_at if hasattr(ach, 'created_at') else None
        }
        for ach in action_achievements
    ]

    return Response(data)
