from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
    url(r'^$', views.spiral, name='home'),
    url(r'^analyze', views.spiral, name='analyze'),
    url(r'^rate_limit', views.RateLimitView.as_view(), name='rate_limit'),
    url(r'^autocomplete.json', views.autocomplete, name='autocomplete'),
    (r'^auth/', include('djsite.tweetspiral.auth.urls'))
)
