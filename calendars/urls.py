from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^oauth2callback$', views.oauth2callback, name='oauth2callback'),
    url(r'^add_calendar$', views.add_calendar, name='add_calendar'),
    url(r'^add_merged_calendar$', views.add_merged_calendar, name='add_merged_calendar'),
    url(r'^update_access$', views.update_access, name='update_access'),
    url(r'^account/logout/$', views.logout),
]