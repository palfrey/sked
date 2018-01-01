from django.contrib import admin
from .models import *

admin.site.register(GoogleUser)
admin.site.register(GoogleCalendar)
admin.site.register(IcalCalendar)