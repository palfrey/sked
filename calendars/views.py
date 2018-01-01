from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpRequest
from django.db import transaction
from django.conf import settings
from django.urls import reverse
import datetime

import google.oauth2.credentials
import google_auth_oauthlib.flow
from apiclient.discovery import build
from .models import *

import requests

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

def home(request):
    email = request.session.get("email", None)
    if email is not None:
        try:
            user = GoogleUser.objects.get(email=email)
        except GoogleUser.DoesNotExist:
            del request.session["email"]
            return redirect(reverse("home"))
        calendars = list(user.calendars.all())
        data = {"user": user, "calendars": calendars}
    else:
        flow = make_flow(request)

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent')
        request.session['state'] = state
        data = {'user': None, 'auth_url': authorization_url}
    return render(request, 'home.html', data)

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


def logout(request):
    raise Exception
    #logout(request)
    return HttpResponseRedirect('/')