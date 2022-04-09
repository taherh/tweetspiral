# Copyright (c) 2012 Taher Haveliwala
# All Rights Reserved
#
# See LICENSE for licensing
#

from django.urls import *
from . import views

urlpatterns = [
    path('', views.spiral, name='home'),
    path('analyze', views.spiral, name='analyze'),
    path('rate_limit', views.RateLimitErrorView.as_view(), name='rate_limit_error'),
    path('error', views.GeneralErrorView.as_view(), name='error'),
    path('autocomplete.json', views.autocomplete, name='autocomplete'),
    path('users_lookup.json', views.users_lookup, name='users_lookup'),
    path('auth/', include('djsite.tweetspiral.auth.urls'))
]
