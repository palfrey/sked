# Generated by Django 2.2.13 on 2020-06-28 22:04

import calendars.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendars', '0005_icaltype_specify'),
    ]

    operations = [
        migrations.AlterField(
            model_name='icalcalendar',
            name='icalType',
            field=models.CharField(choices=[(calendars.models.IcalType('Generic'), 'Generic'), (calendars.models.IcalType('WhosOff'), 'WhosOff'), (calendars.models.IcalType('BambooHR'), 'BambooHR')], max_length=7),
        ),
    ]