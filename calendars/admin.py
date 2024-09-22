from django.contrib import admin

from .models import (
    CalendarAccess,
    GoogleCalendar,
    GoogleUser,
    IcalCalendar,
    MergedCalendar,
)

admin.site.register(GoogleUser)
admin.site.register(GoogleCalendar)
admin.site.register(IcalCalendar)
admin.site.register(MergedCalendar)
admin.site.register(CalendarAccess)
