# Generated by Django 2.0 on 2018-01-01 22:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calendars', '0004_auto_20180101_2130'),
    ]

    operations = [
        migrations.CreateModel(
            name='IcalCalendar',
            fields=[
                ('url', models.URLField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('last_retrieved_at', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='i_calendars', to='calendars.GoogleUser')),
            ],
        ),
        migrations.AlterField(
            model_name='googlecalendar',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='g_calendars', to='calendars.GoogleUser'),
        ),
    ]