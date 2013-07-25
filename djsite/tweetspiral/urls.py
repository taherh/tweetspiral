# Copyright (c) 2012 Taher Haveliwala
# All Rights Reserved
#
# See LICENSE for licensing
#

from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
    url(r'^$', views.spiral, name='home'),
    url(r'^analyze', views.spiral, name='analyze'),
    url(r'^rate_limit', views.RateLimitErrorView.as_view(), name='rate_limit_error'),
    url(r'^error', views.GeneralErrorView.as_view(), name='error'),
    url(r'^autocomplete.json', views.autocomplete, name='autocomplete'),
    url(r'^users_lookup.json', views.users_lookup, name='users_lookup'),
    (r'^auth/', include('djsite.tweetspiral.auth.urls'))
)
