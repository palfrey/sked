# Generated by Django 5.1.1 on 2024-09-26 22:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("calendars", "0007_icaltype_longer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="icalcalendar",
            name="icalType",
            field=models.CharField(
                choices=[
                    ("IcalType.GENERIC", "Generic"),
                    ("IcalType.WHOSOFF", "WhosOff"),
                    ("IcalType.BAMBOO", "BambooHR"),
                ],
                max_length=32,
            ),
        ),
    ]
