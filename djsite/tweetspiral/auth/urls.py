# Copyright (c) 2012 Taher Haveliwala
# All Rights Reserved
#
# See LICENSE for licensing
#

from django.conf.urls import *
from . import views

urlpatterns = patterns('',
    url(r'^login$', views.login, name='login'),
    url(r'^callback$', views.callback, name='callback'),
    url(r'^logout$', views.logout, name='logout')
)