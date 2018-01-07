from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('oauth2callback', views.oauth2callback, name='oauth2callback'),
    path('add_calendar', views.add_calendar, name='add_calendar'),
    path('add_merged_calendar', views.add_merged_calendar, name='add_merged_calendar'),
    path('calendar/<uuid:id>', views.merged_calendar, name='merged_calendar'),
    path('update_access', views.update_access, name='update_access'),
    path('account/logout/', views.logout),
]