# Copyright (c) 2012 Taher Haveliwala
# All Rights Reserved
#
# See LICENSE for licensing
#

from django.conf.urls.defaults import *
from . import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'', include('djsite.tweetspiral.urls'))
    # Example:
    # (r'^djsite/', include('djsite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
