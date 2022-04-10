# Copyright (c) 2012 Taher Haveliwala
# All Rights Reserved
#
# See LICENSE for licensing
#

import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django import http

from .forms import *
from .spiralengine import SpiralEngine
from .autocomplete import AutocompleteEngine
from .exceptions import *
from .util import error_check
import tweepy

@error_check
def spiral(request):
    
    spiral_engine = SpiralEngine(request, AutocompleteEngine(request))

    tpl_data = {}
    tpl_data['tweet_url'] = request.build_absolute_uri()
    
    if spiral_engine.logged_in:
        me = spiral_engine.api.verify_credentials()
        tpl_data['me'] = me

        if not request.session.get('ac_friends', False):
            my_friends_ids = spiral_engine.lookup_friends(user=me)
            my_friends = sorted(
                spiral_engine.lookup_users(user_ids=my_friends_ids, limit=1000),
                key=lambda user: user.followers_count,
                reverse=True
            )
    
            spiral_engine.ac_engine.add_suggestions(me.screen_name)
            spiral_engine.ac_engine.add_suggestions(friend.screen_name for friend in my_friends[0:1000])
            request.session['ac_friends'] = True

    if request.method == 'GET' and len(request.GET) > 0:
        form = SpiralForm(request.GET)
        tpl_data['form'] = form
        if form.is_valid():
            clean_data = form.cleaned_data
            command = clean_data['command']

            # format the mentions panel accordingly (this should go in
            # template if templates supported this sort of logic)
            if command in ("friend_overlap", "follower_overlap"):
                tpl_data['mention_cols'] = 3
            elif command in ("group_profile"):
                tpl_data['mention_cols'] = 5
                
            result = spiral_engine.process(command, clean_data)
            tpl_data.update(result)
   
            return render(request, 'spiral.html', tpl_data)
        else:
            return render(request, 'spiral.html', tpl_data)
    else:
        form = SpiralForm()
        tpl_data['form'] = form
        return render(request, 'spiral.html', tpl_data)        

def autocomplete(request):
    '''Handles autocomplete requests
    
    Input:
        GET var 'term' containing partial term.
    
    Returns:
        List of suggested term completions (JSON format)
    '''
    
    autocomplete_engine = AutocompleteEngine(request)
    
    content = {}
    if request.method == 'GET' and len(request.GET) > 0:
        form = AutocompleteForm(request.GET)
        if form.is_valid():
            clean_data = form.cleaned_data
            term_list = autocomplete_engine.suggest(clean_data['term'])[0:10]
            content = json.dumps(term_list)

    return http.HttpResponse(
        content, content_type='application/json')

def users_lookup(request):
    '''Proxy for twitter api 1.1 'users/lookup' necessary for server-side
       authentication for jquery.hovercard client code'''

    content = {}
    if request.method == 'GET' and len(request.GET) > 0:
        # raw_api=True will tell the api to pass back raw, unparsed results that
        # we can return directly
        spiral_engine = SpiralEngine(request, AutocompleteEngine(request), raw_api=True)
        content = spiral_engine.api.lookup_users(screen_name=request.GET['screen_name'].split(','))
        
    return http.HttpResponse(
        content, content_type='application/json'
    )

class SpiralErrorView(TemplateView):
    def get_context_data(self, *args, **kwargs):
        context = super(SpiralErrorView, self).get_context_data(*args, **kwargs)
        try:
            spiral_engine = SpiralEngine(self.request, None)
        
            tpl_data = {}
            if spiral_engine.logged_in:
                tpl_data['me'] = spiral_engine.api.me()
                tpl_data['logged_in'] = True
            else:
                tpl_data['logged_in'] = False

            context.update(tpl_data)
        except Exception as e:
            print("Exception in SpiralErrorView: %r" % e)
            if settings.DEBUG: raise
        return context
    
class RateLimitErrorView(SpiralErrorView):
    template_name = "rate_limit.html"

class GeneralErrorView(SpiralErrorView):
    template_name = "error.html"

