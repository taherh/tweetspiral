from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
    url(r'^login$', views.login, name='login'),
    url(r'^callback$', views.callback, name='callback'),
    url(r'^logout$', views.logout, name='logout')
)