# Generated by Django 4.2.19 on 2025-03-04 14:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0006_remove_dish_cereals_remove_dish_chickpeas_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="meal",
            name="Chicken",
            field=models.IntegerField(default=0, null=True),
        ),
    ]
