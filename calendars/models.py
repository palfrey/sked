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

    def __str__(self):
        return self.name

class IcalCalendar(models.Model):
    url = models.URLField(primary_key=True)
    user = models.ForeignKey(GoogleUser, on_delete=models.CASCADE, related_name='i_calendars')
    name = models.CharField(max_length=255)
    last_retrieved_at = models.DateTimeField()

    def __str__(self):
        return self.name

NO_ACCESS = 'no'

class MergedCalendar(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(GoogleUser, on_delete=models.CASCADE, related_name='m_calendars')

    def __str__(self):
        return '%s for %s' % (self.name, self.user.name)

    def get_access(self, calendar):
        entries = list(calendar.access.all())
        for ac in entries:
            if ac.mergedCalendar == self:
                return ac
        return CalendarAccess(access_level=NO_ACCESS)

class CalendarAccess(models.Model):
    mergedCalendar = models.ForeignKey(MergedCalendar, on_delete=models.CASCADE, related_name='access')

    # Only one of these two should be non-null
    g_calendar = models.ForeignKey(GoogleCalendar, on_delete=models.CASCADE, related_name='access', null=True, blank=True)
    i_calendar = models.ForeignKey(IcalCalendar, on_delete=models.CASCADE, related_name='access', null=True, blank=True)

    ACCESS_CHOICES = (
        (NO_ACCESS, 'No'),
        ('busy', 'Busy'),
        ('yes', 'Yes'),
    )
    access_level = models.CharField(choices=ACCESS_CHOICES, default=NO_ACCESS, max_length=4)

    def __str__(self):
        cal = self.i_calendar if self.g_calendar == None else self.g_calendar
        return "Access is '%s' to '%s' for %s" % (self.access_level, cal, self.mergedCalendar)