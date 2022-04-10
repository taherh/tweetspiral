# Copyright (c) 2012 Taher Haveliwala
# All Rights Reserved
#
# See LICENSE for licensing
#

from django.http import *
from django.shortcuts import render, redirect
from django.contrib.auth import logout as django_logout
from django.urls import reverse
from django.conf import settings
import tweepy

def logout(request):
    django_logout(request)  # calls request.session.flush()
    return redirect('home')
    
def login(request):
    callback = request.build_absolute_uri(reverse('callback'))
    oauth = tweepy.OAuth1UserHandler(settings.TWITTER_CONSUMER_KEY,
                                settings.TWITTER_CONSUMER_SECRET,
                                callback=callback)
    auth_url = oauth.get_authorization_url(False)

    request.session['request_token_tw'] = (oauth.request_token["oauth_token"],
                                           oauth.request_token["oauth_token_secret"]) 

    return redirect(auth_url)

def callback(request):
    oauth = tweepy.OAuth1UserHandler(settings.TWITTER_CONSUMER_KEY,
                                settings.TWITTER_CONSUMER_SECRET,
                                callback=None)


    # get the request token from the session cookie (then remove from cookie)
    session_token = request.session['request_token_tw']
    request.session.delete('request_token_tw')

    oauth.request_token = {
        "oauth_token": session_token[0],
        "oauth_token_secret": session_token[1]
    }

    verifier = request.GET.get('oauth_verifier')

    # get the access token and store
    try:
        access_token, access_token_secret = oauth.get_access_token(verifier)
    except tweepy.TweepyException:
        print('Error, failed to get access token')

    try:
        request.session['access_token_tw'] = access_token
        request.session['access_token_secret_tw'] = access_token_secret
    except Exception:
        return redirect('home')
        
    return redirect('home')
