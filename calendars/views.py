from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse

import google.oauth2.credentials
import google_auth_oauthlib.flow
from apiclient.discovery import build
from .models import *
from .forms import *

import requests
import icalendar
import datetime
from functools import wraps
import iso8601

scopes = ['https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/calendar.readonly']

def about_sked(request):
    return render(request, 'about_sked.html')

def guide(request):
    return render(request, 'guide.html')

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
                "m_calendars": list(user.m_calendars.all()),
                "total_cals": user.g_calendars.count() + user.i_calendars.count()}
    else:
        flow = make_flow(request)

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent')
        request.session['state'] = state
        data = {'user': None, 'auth_url': authorization_url}
    return render(request, 'home.html', data)

def update_access_core(request, user):
    for mc in user.m_calendars.all():
        for ac in mc.access.all():
            if str(ac.id) in request.POST:
                ac.access_level = request.POST[str(ac.id)]
                ac.save()
    messages.success(request, 'Permissions updated')

@needs_login
def update_access(request, user=None):
    update_access_core(request, user)
    return redirect(reverse('home'))

@needs_login
def update_access_merged(request, id, user=None):
    update_access_core(request, user)
    return redirect(reverse('merged_calendar', args=[id]))

def get_gcalendars(credentials):
    calendar_service = build(
        serviceName='calendar', version='v3',
        credentials=credentials)
    return calendar_service.calendarList().list(minAccessRole="reader").execute()['items']

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
        calendars = get_gcalendars(credentials)
        for calendar in calendars:
            cal, created = GoogleCalendar.objects.get_or_create(id=calendar['id'], user=user, name=calendar['summary'], primary=calendar.get('primary', False))
            cal.save()
        user.calendars_retrieved_at = datetime.datetime.now()
        user.save()
    return redirect(reverse('home'))

@needs_login
def refresh_gcalendars(request, user=None):
    credentials = make_credentials(user)
    calendars = get_gcalendars(credentials)
    existing_calendars = dict([(cal.id, cal) for cal in user.g_calendars.all()])
    for calendar in calendars:
        id = calendar['id']
        if id in existing_calendars:
            del existing_calendars[id]
        else:
            cal, _ = GoogleCalendar.objects.get_or_create(id=calendar['id'], user=user, name=calendar['summary'], primary=calendar.get('primary', False))
            cal.save()
    user.calendars_retrieved_at = datetime.datetime.now()
    user.save()
    for calendar in existing_calendars.values():
        calendar.delete()
    messages.success(request, "Google Calendars updated")
    return redirect(reverse('home'))

@needs_login
def add_calendar(request, user=None):
    if request.method == 'POST':
        form = NewCalendarForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['calendar_url']
            url = url.replace("webcal://", "http://")
            try:
                cal = requests.get(url)
                if cal.status_code == 200:
                    try:
                        parsed = icalendar.Calendar.from_ical(cal.text)
                        new_cal, _ = IcalCalendar.objects.get_or_create(url=url, user=user, defaults={'last_retrieved_at': datetime.datetime.now()})
                        new_cal.name = parsed.get('X-WR-CALNAME', "")
                        new_cal.last_retrieved_at = datetime.datetime.now()
                        new_cal.save()
                        messages.success(request, "Calendar '%s' added" % new_cal.name)
                        return redirect(reverse('home'))
                    except ValueError:
                        form.add_error("calendar_url", "Bad iCal file at %s (or possibly not one at all)" % url)
                else:
                    form.add_error("calendar_url", "Bad response from %s: %s - %s" % (url, cal.status_code, cal.reason))
            except:
                form.add_error("calendar_url", "Error getting %s" % url)
    else:
        form = NewCalendarForm()
    return render(request, "new_calendar.html", {"form": form})

@needs_login
def add_merged_calendar(request, user=None):
    if request.method == 'POST':
        form = MergedCalendarForm(request.POST)
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
        form = MergedCalendarForm()
    return render(request, "new_merged_calendar.html", {"form": form})

@needs_login
def merged_calendar(request, id, user=None):
    mc = get_object_or_404(MergedCalendar, id=id)
    if mc.user != user:
        return redirect(reverse('home'))
    if request.method == 'POST':
        form = MergedCalendarForm(request.POST)
        if form.is_valid():
            mc.name = form.cleaned_data['name']
            messages.success(request, "Updated name to '%s'" % mc.name)
            mc.save()
    else:
        form = MergedCalendarForm({"name":mc.name})
    return render(request, "merged_calendar.html", {"user": user, "mc": mc, "form": form, "url": request.build_absolute_uri(reverse("merged_calendar_view", args=[mc.id]))})

@needs_login
def my_calendar(request, user=None):
    return render(request, "my_calendar.html", {"user": user})

@needs_login
def my_calendar_json(request, user=None):
    res = icalendar.Calendar()
    res.add('prodid', '-//Sked//')
    res.add('version', '2.0')
    res.add('X-WR-CALNAME', user.name)
    for gcal in user.g_calendars.all():
        add_gcalendar(res, gcal.id, "yes", user)
    for ical in user.i_calendars.all():
        add_icalendar(res, ical.url, "yes")
    return calendar_json_core(request, res)

def date_convert(when):
    if 'dateTime' in when:
        return icalendar.vDatetime(iso8601.parse_date(when['dateTime']))
    elif 'date' in when:
        return icalendar.vDate(iso8601.parse_date(when['date']))
    else:
        raise Exception(when)

def add_event(cal, event, access_level):
    if access_level == "yes":
        pass
    elif access_level == "alld":
        if event['dtstart'].dt.hour != 0:
            return
    elif access_level == 'busy':
        if 'summary' in event:
            event['summary'] = 'BUSY'
        if 'description' in event:
            event['description'] = 'BUSY'
        for x in ['location', 'organizer', 'url']:
            if x in event:
                del event[x]
    else:
        raise Exception(event)
    cal.add_component(event)

def add_gcalendar(main_cal, id, access_level, user):
    minTime = (datetime.datetime.now()-datetime.timedelta(days=30)).isoformat() + 'Z'
    maxTime = (datetime.datetime.now()+datetime.timedelta(days=365)).isoformat() + 'Z'
    items = cache.get(id)
    if items == None:
        credentials = make_credentials(user)
        calendar_service = build(
            serviceName='calendar', version='v3',
            credentials=credentials)
        items = []
        pageToken = None
        while True:
            eventsResult = calendar_service.events().list(calendarId=id, timeMin=minTime, timeMax=maxTime, singleEvents=True, maxResults=2500, pageToken=None).execute()
            items += eventsResult["items"]
            if "nextPageToken" not in eventsResult:
                break
            pageToken = eventsResult["nextPageToken"]
        cache.set(id, items)
    for item in items:
        if item['status'] == 'cancelled':
            continue
        event = icalendar.Event()
        event.add('summary', item['summary'])
        event.add('dtstart', date_convert(item['start']))
        event.add('dtend', date_convert(item['end']))
        try:
            event.add('dtstamp', iso8601.parse_date(item['created']))
        except iso8601.ParseError:
            pass
        if 'organizer' in item:
            organiser = icalendar.vCalAddress(item['organizer']['email'])
            if 'displayName' in item['organizer']:
                organiser.params['cn'] = icalendar.vText(item['organizer']['displayName'])
            event.add('organizer', organiser)
        event['uid'] = item['iCalUID']
        add_event(main_cal, event, access_level)

def add_icalendar(main_cal, url, access_level):
    ical = cache.get(url)
    if ical == None:
        data = requests.get(url)
        if not data.ok:
            return
        ical = data.text
        cache.set(url, ical)
    cal = icalendar.Calendar.from_ical(ical)
    for event in cal.subcomponents:
        add_event(main_cal, event, access_level)

def merged_calendar_core(id):
    mc = get_object_or_404(MergedCalendar, id=id)
    main_cal = icalendar.Calendar()
    main_cal.add('prodid', '-//Sked//')
    main_cal.add('version', '2.0')
    main_cal.add('X-WR-CALNAME', mc.user.name)

    for ac in mc.access.all():
        if ac.access_level == 'no':
            continue
        if ac.g_calendar != None:
            add_gcalendar(main_cal, ac.g_calendar.id, ac.access_level, mc.user)
        elif ac.i_calendar != None:
            add_icalendar(main_cal, ac.i_calendar.url, ac.access_level)
        else:
            raise Exception(ac)
    return main_cal

def merged_calendar_view(request, id):
    main_cal = merged_calendar_core(id)
    return HttpResponse(main_cal.to_ical())

def calendar_json_core(request, res):
    start = iso8601.parse_date(request.GET['start'])
    end = iso8601.parse_date(request.GET['end'])
    events = []
    for event in res.subcomponents:
        if 'dtstart' not in event:
            continue
        if event['dtstart'].dt >= start and event['dtstart'].dt < end:
            derived = {'start': event['dtstart'].dt, 'end': event['dtend'].dt, 'title': event['summary']}
            if 'url' in event:
                derived['url'] = event['url']
            if event['dtstart'].dt.hour == 0:
                derived['allDay'] = True
            events.append(derived)
    return JsonResponse(events, safe=False, json_dumps_params={"indent": 4})

def merged_calendar_json(request, id):
    res = merged_calendar_core(id)
    return calendar_json_core(res)

@needs_login
@require_POST
def delete_merged_calendar(request, id, user=None):
    mc = get_object_or_404(MergedCalendar, id=id)
    if mc.user != user:
        return redirect(reverse('home'))
    mc.delete()
    messages.success(request, "Deleted '%s'" % mc.name)
    return redirect(reverse('home'))

@needs_login
@require_POST
def delete_calendar(request, id, user=None):
    ic = get_object_or_404(IcalCalendar, id=id)
    if ic.user != user:
        return redirect(reverse('home'))
    ic.delete()
    messages.success(request, "Deleted '%s'" % ic.name)
    return redirect(reverse('home'))

def logout(request):
    del request.session["email"]
    return redirect(reverse('home'))