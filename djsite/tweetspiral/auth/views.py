# Copyright (c) 2012 Taher Haveliwala
# All Rights Reserved
#
# See LICENSE for licensing
#

from django.http import *
from django.shortcuts import render, redirect
from django.contrib.auth import logout as django_logout
from django.core.urlresolvers import reverse
from django.conf import settings
import tweepy

def logout(request):
    django_logout(request)  # calls request.session.flush()
    return redirect('home')
    
def login(request):
    callback = request.build_absolute_uri(reverse('callback'))
    oauth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY,
                                settings.TWITTER_CONSUMER_SECRET,
                                callback=callback, secure=True)
    auth_url = oauth.get_authorization_url(False)
    request.session['request_token_tw'] = (oauth.request_token.key,
                                           oauth.request_token.secret)
    return redirect(auth_url)

def callback(request):
    verifier = request.GET.get('oauth_verifier')
    oauth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY,
                                settings.TWITTER_CONSUMER_SECRET,
                                callback=None, secure=True)
    token = request.session.get('request_token_tw', None)
    # remove the request token now we don't need it
    request.session.delete('request_token_tw')
    oauth.set_request_token(token[0], token[1])
    # get the access token and store
    try:
    	oauth.get_access_token(verifier)
    except tweepy.TweepError:
    	print 'Error, failed to get access token'

    try:
        request.session['access_token_tw'] = oauth.access_token.key
        request.session['access_token_secret_tw'] = oauth.access_token.secret
    except Exception:
        return redirect('home')
        
    return redirect('home')
