# Generated by Django 2.0 on 2018-01-06 16:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calendars', '0006_mergedcalendar'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalendarAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_level', models.CharField(choices=[('no', 'No'), ('busy', 'Busy'), ('yes', 'Yes')], default='no', max_length=4)),
                ('g_calendar', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='access', to='calendars.GoogleCalendar')),
                ('i_calendar', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='access', to='calendars.IcalCalendar')),
                ('mergedCalendar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access', to='calendars.MergedCalendar')),
            ],
        ),
    ]
