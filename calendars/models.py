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
    user = models.ForeignKey(GoogleUser, on_delete=models.CASCADE, related_name='g_calendars')
    name = models.CharField(max_length=255)
    primary = models.BooleanField()

class IcalCalendar(models.Model):
    url = models.URLField(primary_key=True)
    user = models.ForeignKey(GoogleUser, on_delete=models.CASCADE, related_name='i_calendars')
    name = models.CharField(max_length=255)
    last_retrieved_at = models.DateTimeField()

class MergedCalendar(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(GoogleUser, on_delete=models.CASCADE, related_name='m_calendars')

    def __str__(self):
        return '%s for %s' % (self.name, self.user.name)