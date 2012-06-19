from django.http import *
from django.shortcuts import render, redirect
from django.contrib.auth import logout as django_logout
from django.core.urlresolvers import reverse
from .oauth_settings import CONSUMER_KEY, CONSUMER_SECRET
import tweepy

def logout(request):
    request.session.flush()
    response = django_logout(request)  # probably does nothing since we didn't "django_login"
    return redirect('home')
    
def login(request):
    callback = request.build_absolute_uri(reverse('callback'))
    oauth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, callback=callback)
    auth_url = oauth.get_authorization_url(False)
    request.session['request_token_tw'] = (oauth.request_token.key,
                                           oauth.request_token.secret)
    return redirect(auth_url)

def callback(request):
    verifier = request.GET.get('oauth_verifier')
    oauth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
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
