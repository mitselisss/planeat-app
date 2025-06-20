# Generated by Django 4.2.19 on 2025-06-19 08:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app", "0031_remove_userachievementscalculation_points"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserActionAchievements",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_date", models.DateField(blank=True, null=True)),
                ("day", models.CharField(default="", max_length=255)),
                ("action", models.CharField(default="", max_length=255)),
                ("reason", models.CharField(default="", max_length=255, null=True)),
                ("points", models.IntegerField(default=0, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="userprofile",
            name="Main_screen",
            field=models.CharField(default="daily", max_length=10),
        ),
        migrations.DeleteModel(
            name="UserAchievementsCalculation",
        ),
    ]
