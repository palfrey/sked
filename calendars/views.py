from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.db import transaction
from .models import Profile
from .forms import UserForm,ProfileForm

import oauth2client.client
import httplib2
import requests

@login_required
def Home(request):
    social = request.user.social_auth.get(provider='google-oauth2')
    resp = requests.get("https://www.googleapis.com/calendar/v3/users/me/calendarList?minAccessRole=owner", headers={"Authorization": "Bearer %s" % social.extra_data["access_token"]})
    # credentials = oauth2client.client.AccessTokenCredentials(social.extra_data['access_token'],
    #     'my-user-agent/1.0')
    # http = httplib2.Http()
    # http = credentials.authorize(http)
    # resp = http.request('https://www.googleapis.com/calendar/v3/users/me/calendarList?minAccessRole=owner')
    return render(request, 'home.html', {'data': social.extra_data})

@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect('/')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def Logout(request):
    logout(request)
    return HttpResponseRedirect('/')