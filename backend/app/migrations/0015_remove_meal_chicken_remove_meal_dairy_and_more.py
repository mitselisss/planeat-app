# Generated by Django 4.2.19 on 2025-03-07 10:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0014_remove_meal_a_remove_meal_aa_remove_meal_ab_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="meal",
            name="Chicken",
        ),
        migrations.RemoveField(
            model_name="meal",
            name="Dairy",
        ),
        migrations.RemoveField(
            model_name="meal",
            name="Fish",
        ),
        migrations.RemoveField(
            model_name="meal",
            name="Fruit",
        ),
        migrations.RemoveField(
            model_name="meal",
            name="Meat",
        ),
        migrations.RemoveField(
            model_name="meal",
            name="Nuts_and_seeds",
        ),
        migrations.RemoveField(
            model_name="meal",
            name="Plant_protein",
        ),
        migrations.RemoveField(
            model_name="meal",
            name="Vegetables",
        ),
    ]
