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

def make_flow(request):
    callback = request.build_absolute_uri(reverse('oauth2callback'))
    oauth_config = {'web': {
                    'client_id': settings.GOOGLE_OAUTH2_KEY,
                    'client_secret': settings.GOOGLE_OAUTH2_SECRET,
                    "redirect_uris": [callback],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://accounts.google.com/o/oauth2/token"
                    }}
    scopes = ['https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/calendar.readonly']
    return google_auth_oauthlib.flow.Flow.from_client_config(oauth_config,
            scopes=scopes, redirect_uri=callback)

def home(request):
    email = request.session.get("email", None)
    if email is not None:
        user = GoogleUser.objects.get(email=email)
        authorization_url = None
    else:
        flow = make_flow(request)

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true')
        request.session['state'] = state
        user = None
    #social = request.user.social_auth.get(provider='google-oauth2')
    #resp = requests.get("https://www.googleapis.com/calendar/v3/users/me/calendarList?minAccessRole=owner", headers={"Authorization": "Bearer %s" % social.extra_data["access_token"]})
    # credentials = oauth2client.client.AccessTokenCredentials(social.extra_data['access_token'],
    #     'my-user-agent/1.0')
    # http = httplib2.Http()
    # http = credentials.authorize(http)
    # resp = http.request('https://www.googleapis.com/calendar/v3/users/me/calendarList?minAccessRole=owner')
    return render(request, 'home.html', {'user': user, 'auth_url': authorization_url})

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
    # cred = {
    #     'token': credentials.token,
    #     'refresh_token': credentials.refresh_token,
    #     'token_uri': credentials.token_uri,
    #     'client_id': credentials.client_id,
    #     'client_secret': credentials.client_secret,
    #     'scopes': credentials.scopes}
    return redirect(reverse('home'))


def logout(request):
    raise Exception
    #logout(request)
    return HttpResponseRedirect('/')