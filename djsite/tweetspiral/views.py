import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django import http

from .forms import *
from .spiralengine import SpiralEngine
from .autocomplete import AutocompleteEngine
from .exceptions import *
from .util import rate_limit_check
import tweepy

@rate_limit_check
def spiral(request):
    
    ac_engine = AutocompleteEngine(request)
    spiral_engine = SpiralEngine(request, ac_engine)

    tpl_data = {}
    tpl_data['tweet_url'] = request.build_absolute_uri()
    
    if spiral_engine.logged_in:
        me = spiral_engine.api.me()
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
                
            try:
                result = spiral_engine.process(command, clean_data)
            except RateLimitError as e:
                return redirect('rate_limit')
            except Exception as e:
                print("Exception: %s" % e)
                if settings.DEBUG: raise
            else:
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

class RateLimitView(TemplateView):
    template_name = "rate_limit.html"
