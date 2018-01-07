from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.conf import settings
from django.urls import reverse
from django.contrib import messages

import google.oauth2.credentials
import google_auth_oauthlib.flow
from apiclient.discovery import build
from .models import *
from .forms import *

import requests
import icalendar
import datetime
from functools import wraps

scopes = ['https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/calendar.readonly']

def make_flow(request):
    callback = request.build_absolute_uri(reverse('oauth2callback'))
    oauth_config = {'web': {
                    'client_id': settings.GOOGLE_OAUTH2_KEY,
                    'client_secret': settings.GOOGLE_OAUTH2_SECRET,
                    "redirect_uris": [callback],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://accounts.google.com/o/oauth2/token"
                    }}
    return google_auth_oauthlib.flow.Flow.from_client_config(oauth_config,
            scopes=scopes, redirect_uri=callback)

def make_credentials(user):
    cred = {
        'token': user.token,
        'refresh_token': user.refresh_token,
        'token_uri': "https://accounts.google.com/o/oauth2/token",
        'client_id': settings.GOOGLE_OAUTH2_KEY,
        'client_secret': settings.GOOGLE_OAUTH2_SECRET,
        'scopes': scopes}
    credentials = google.oauth2.credentials.Credentials(**cred)
    return credentials

class Redirect(Exception):
    def __init__(self, url):
        self.url = url

def get_user(request):
    email = request.session.get("email", None)
    if email is not None:
        try:
            return GoogleUser.objects.get(email=email)
        except GoogleUser.DoesNotExist:
            del request.session["email"]
            raise Redirect(reverse("home"))
    else:
        return None

def needs_login(view_func):
    def _decorator(request, *args, **kwargs):
        try:
            user = get_user(request)
        except Redirect as r:
            return redirect(r.url)
        if user == None:
            return redirect(reverse('home'))
        kwargs['user'] = user
        response = view_func(request, *args, **kwargs)
        return response
    return wraps(view_func)(_decorator)

def home(request):
    try:
        user = get_user(request)
    except Redirect as r:
        return redirect(r.url)
    if user:
        data = {"user": user,
                "g_calendars": list(user.g_calendars.all()),
                "i_calendars": list(user.i_calendars.all()),
                "m_calendars": list(user.m_calendars.all())}
    else:
        flow = make_flow(request)

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent')
        request.session['state'] = state
        data = {'user': None, 'auth_url': authorization_url}
    return render(request, 'home.html', data)

@needs_login
def update_access(request, user=None):
    for mc in user.m_calendars.all():
        for ac in mc.access.all():
            if str(ac.id) in request.POST:
                ac.access_level = request.POST[str(ac.id)]
                ac.save()
    messages.success(request, 'Permissions updated')
    return redirect(reverse('home'))

def oauth2callback(request):
    state = request.session['state']
    flow = make_flow(request)
    flow.state = state
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    user_info_service = build(
        serviceName='oauth2', version='v2',
        credentials=credentials)
    user_info = user_info_service.userinfo().get().execute()

    user, created = GoogleUser.objects.get_or_create(email=user_info['email'])
    user.token = credentials.token
    user.refresh_token = credentials.refresh_token
    user.name = user_info['name']
    user.save()
    request.session['email'] = user.email
    if created:
        calendar_service = build(
            serviceName='calendar', version='v3',
            credentials=credentials)
        calendars = calendar_service.calendarList().list(minAccessRole="owner").execute()['items']
        for calendar in calendars:
            cal, created = GoogleCalendar.objects.get_or_create(id=calendar['id'], user=user, name=calendar['summary'], primary=calendar.get('primary', False))
            cal.save()
        user.calendars_retrieved_at = datetime.datetime.now()
        user.save()
    return redirect(reverse('home'))

@needs_login
def add_calendar(request, user=None):
    if request.method == 'POST':
        form = NewCalendarForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['calendar_url']
            cal = requests.get(url)
            if cal.status_code == 200:
                try:
                    parsed = icalendar.Calendar.from_ical(cal.text)
                    new_cal, _ = IcalCalendar.objects.get_or_create(url=url, user=user, defaults={'last_retrieved_at': datetime.datetime.now()})
                    new_cal.name = parsed.get('X-WR-CALNAME', "")
                    new_cal.last_retrieved_at = datetime.datetime.now()
                    new_cal.save()
                    messages.success(request, 'Calendar added')
                    return redirect(reverse('home'))
                except ValueError:
                    form.add_error("calendar_url", "Bad iCal file at %s (or possibly not one at all)" % url)
            else:
                form.add_error("calendar_url", "Bad response from %s: %s - %s" % (url, cal.status_code, cal.reason))
    else:
        form = NewCalendarForm()
    return render(request, "new_calendar.html", {"form": form})

@needs_login
def add_merged_calendar(request, user=None):
    if request.method == 'POST':
        form = NewMergedCalendarForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            if MergedCalendar.objects.filter(name=name, user=user).exists():
                form.add_error("name", "Calendar called '%s' already exists" % name)
            else:
                m = MergedCalendar(name=name, user=user)
                m.save()
                messages.success(request, "Merged calendar added for '%s'" % name)
                return redirect(reverse('home'))
    else:
        form = NewMergedCalendarForm()
    return render(request, "new_merged_calendar.html", {"form": form})

@needs_login
def merged_calendar(request, id, user=None):
    raise Exception


def logout(request):
    raise Exception
    #logout(request)
    return redirect('/')