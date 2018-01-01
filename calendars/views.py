from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpRequest
from django.db import transaction
from django.conf import settings
from django.urls import reverse

import google.oauth2.credentials
import google_auth_oauthlib.flow
from apiclient.discovery import build
from .models import GoogleUser

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
        'refresh_token': None,
        'token_uri': "https://accounts.google.com/o/oauth2/token",
        'client_id': settings.GOOGLE_OAUTH2_KEY,
        'client_secret': settings.GOOGLE_OAUTH2_SECRET,
        'scopes': scopes}
    credentials = google.oauth2.credentials.Credentials(**cred)
    return credentials

def home(request):
    email = request.session.get("email", None)
    if email is not None:
        user = GoogleUser.objects.get(email=email)
        authorization_url = None
        credentials = make_credentials(user)
        calendar_service = build(
            serviceName='calendar', version='v3',
            credentials=credentials)
        calendars = calendar_service.calendarList().list(minAccessRole="owner").execute()['items']
    else:
        flow = make_flow(request)

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true')
        request.session['state'] = state
        user = None
        calendars = []
    return render(request, 'home.html', {'user': user, 'auth_url': authorization_url, 'calendars': calendars})

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

    user, _ = GoogleUser.objects.get_or_create(email=user_info['email'])
    user.token = credentials.token
    user.name = user_info['name']
    user.save()
    request.session['email'] = user.email
    return redirect(reverse('home'))


def logout(request):
    raise Exception
    #logout(request)
    return HttpResponseRedirect('/')