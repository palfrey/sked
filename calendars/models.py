from django.db import models
import datetime

class GoogleUser(models.Model):
    email = models.EmailField(primary_key=True)
    token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    calendars_retrieved_at = models.DateTimeField(default=datetime.datetime.min)

class GoogleCalendar(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    user = models.ForeignKey(GoogleUser, on_delete=models.CASCADE, related_name='calendars')
    name = models.CharField(max_length=255)
    primary = models.BooleanField()