from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.Home),
    url(r'^profile/$', views.update_profile),
    url(r'^account/logout/$', views.Logout),
]