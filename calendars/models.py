import datetime
import uuid
from enum import Enum

from django.db import models


class GoogleUser(models.Model):
    email = models.EmailField(primary_key=True)
    token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    calendars_retrieved_at = models.DateTimeField(default=datetime.datetime.min)

    is_authenticated = True


class GoogleCalendar(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    user = models.ForeignKey(
        GoogleUser, on_delete=models.CASCADE, related_name="g_calendars"
    )
    name = models.CharField(max_length=255)
    primary = models.BooleanField()

    def __str__(self) -> str:
        return self.name


class IcalType(Enum):
    GENERIC = "Generic"
    WHOSOFF = "WhosOff"
    BAMBOO = "BambooHR"


class IcalCalendar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(unique=True)
    user = models.ForeignKey(
        GoogleUser, on_delete=models.CASCADE, related_name="i_calendars"
    )
    name = models.CharField(max_length=255)
    person = models.CharField(
        max_length=255, null=True, blank=True
    )  # only used by WhosOff
    last_retrieved_at = models.DateTimeField()
    icalType = models.CharField(
        max_length=32,
        choices=[(str(tag), tag.value) for tag in IcalType],
    )

    def __str__(self) -> str:
        return self.name


NO_ACCESS = "no"


class MergedCalendar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        GoogleUser, on_delete=models.CASCADE, related_name="m_calendars"
    )

    def __str__(self) -> str:
        return "%s for %s" % (self.name, self.user.name)

    def get_access(self, calendar: GoogleCalendar | IcalCalendar) -> "CalendarAccess":
        entries = list(calendar.access.all())
        for ac in entries:
            if ac.mergedCalendar == self:
                return ac
        ac = CalendarAccess(access_level=NO_ACCESS, mergedCalendar=self)
        if isinstance(calendar, GoogleCalendar):
            ac.g_calendar = calendar
        elif isinstance(calendar, IcalCalendar):
            ac.i_calendar = calendar
        else:
            raise Exception(type(calendar))
        ac.save()
        return ac

    class Meta:
        ordering = ["name"]


class CalendarAccess(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mergedCalendar = models.ForeignKey(
        MergedCalendar, on_delete=models.CASCADE, related_name="access"
    )

    # Only one of these two should be non-null
    g_calendar = models.ForeignKey(
        GoogleCalendar,
        on_delete=models.CASCADE,
        related_name="access",
        null=True,
        blank=True,
    )
    i_calendar = models.ForeignKey(
        IcalCalendar,
        on_delete=models.CASCADE,
        related_name="access",
        null=True,
        blank=True,
    )

    ACCESS_CHOICES = (
        (NO_ACCESS, "No"),
        ("busy", "Busy"),
        ("yes", "Yes"),
        ("alld", "All-day events only"),
    )
    access_level = models.CharField(
        choices=ACCESS_CHOICES, default=NO_ACCESS, max_length=4
    )

    def __str__(self) -> str:
        cal = self.i_calendar if self.g_calendar is None else self.g_calendar
        return "Access is '%s' to '%s' for %s" % (
            self.access_level,
            cal,
            self.mergedCalendar,
        )
