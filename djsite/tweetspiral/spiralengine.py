import re
import os, sys
import math
from collections import defaultdict
from django.conf import settings
from itertools import repeat
from pprint import pprint

import redis
import tweepy
from .autocomplete import AutocompleteEngine
from .exceptions import *

class SpiralEngine(object):
    '''Per-request handler for tweetspiral webapp requests'''
    
    logged_in = False
    ac_engine = None
    
    def __init__(self, request, ac_engine):
        '''Initialize spiral engine request and authenticate if applicable'''

        self.logged_in = False
        self.ac_engine = ac_engine

        auth = None

        # check if we have a login token
        access_token = request.session.get('access_token_tw', None)
        access_token_secret = request.session.get('access_token_secret_tw', None)    
        if access_token and access_token_secret:
            auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY,
                                       settings.TWITTER_CONSUMER_SECRET)
            auth.set_access_token(access_token, access_token_secret)
            self.logged_in = True
        
        if settings.API_CACHE == 'memory':
            cache = tweepy.MemoryCache(timeout=settings.API_CACHE_TIMEOUT)
        elif settings.API_CACHE == 'file':
            cache = tweepy.FileCache(cache_dir=settings.API_FILE_CACHE_PATH,
                                     timeout=settings.API_CACHE_TIMEOUT)
        elif settings.API_CACHE == 'redis':
            cache = tweepy.RedisCache(redis.StrictRedis(),
                                      timeout=settings.API_CACHE_TIMEOUT)
        else:
            cache = None
    
        self.api = tweepy.API(auth, cache=cache, secure=True)
    
    def process(self, command, req_data):
        '''Processes `command`
        
        Params:
            command: command name to dispatch
            req_data: request data
            
        Returns:
            A context dictionary
        '''
        
        # check to see if we're triggering a fake error
        if req_data['trigger_error']:
            raise FakeError("trigger_error: %s" % req_data['trigger_error'])
        
        # check to see if we've exceeded twitter rate limit
        print("rate_limit_status: %d" % self.api.rate_limit_status()['remaining_hits'])
        if self.api.rate_limit_status()['remaining_hits'] < 10 or \
           req_data['trigger_rate_limit']:
            raise(RateLimitError(logged_in=self.logged_in))
        
        if len(req_data['twitter_handles']) > 100:
            print('query length exceeded')
            result['msgs'] = 'Query length exceeded.'
            return result

        result = {}
        result['command'] = command

        query_screen_names = self._extract_handles(req_data['twitter_handles'])
        input_users = self.lookup_users(screen_names=query_screen_names, step=1)
        input_users = [user for user in input_users if not user.protected]

        self.ac_engine.add_suggestions(query_screen_names)
        
        result['input_users'] = input_users
        if command == "friend_overlap":
            result.update(self.handle_overlap(input_users, "follows"))
        elif command == "follower_overlap":
            for user in input_users:
                if user.followers_count > 10000:
                    result['followers_threshold'] = True
            result.update(self.handle_overlap(input_users, "followers"))
        elif command == "group_profile":
            result.update(self.handle_group_profile(input_users))
        elif command == "similarity":
            result['msgs'] = "Command not yet supported."
        
        if result.get('users', None):
            self.ac_engine.add_suggestions(user.screen_name for user in result['users'])
        if result.get('mentions', None):
            self.ac_engine.add_suggestions(mention.screen_name for mention in result['mentions'])
            
        return result
    
    def handle_overlap(self, input_users, relation_type):
        result = {}
        if relation_type == "follows":
            result['relation_type'] = "follows"
        elif relation_type == 'followers':
            result['relation_type'] = "followers"
        else:
            raise self.UnsupportedRelationError(relation_type)
        
        users = self.compute_overlap(input_users, relation_type)
        
        result['num_results'] = len(users)
        result['users'] = users[0:settings.MAX_OVERLAP_RESULTS]
        statuses = self.get_statuses(input_users)
        statuses.extend((user.status, user.followers_count) for user in users if hasattr(user, 'status'))
        (result['mentions'], result['hashtags']) = self.detect_entities(statuses, limit=9)
        return result
    
    def handle_group_profile(self, input_users):
        result = {}
        result['relation_type'] = "them"
        statuses = self.get_statuses(input_users)
        (result['mentions'], result['hashtags']) = self.detect_entities(statuses, limit=10)
        return result
    
    def _extract_handles(self, handles_string):
        '''Extracts handles from `handles_string`
        
        Params:
            handles_string: string containing handles
        '''
        return re.findall(r"@?(\w+)", handles_string)
        
    def compute_overlap(self, input_users, relation_type):
        '''Compute friend or follower overlaps
        
        Params:
            input_users: list of users
            relation_type: 'follows' or 'followers'
            
        Returns:
            Ranked list of users in overlap
        '''
        
        if relation_type == "follows":
            lookup_fn = self.lookup_friends
        elif relation_type == "followers":
            lookup_fn = self.lookup_followers
        else:
            raise self.UnsupportedRelationError(relation_type)
                
        overlap_id_set = None
        for input_user in input_users:
            try:
                rel_id_set = set(lookup_fn(user=input_user))
            except tweepy.TweepError as e:
                print("TweepError: %s" % e)
                continue
            
            if overlap_id_set is None:
                overlap_id_set = rel_id_set
                continue
            
            overlap_id_set.intersection_update(rel_id_set)
    
        if not overlap_id_set:
            return []
        
        overlap_ids = sorted(overlap_id_set)
        users = self.lookup_users(user_ids=overlap_ids, limit=1000)
    
        # sort by followers_count
        users.sort(key=lambda user: user.followers_count, reverse=True)
    
        return users
    
    def lookup_friends(self, user, limit=20000):
        return tweepy.Cursor(
            self.api.friends_ids, screen_name=user.screen_name, skip_cache_write=user.protected).items(limit=limit)

            
    def lookup_followers(self, user, limit=20000):
        return tweepy.Cursor(
            self.api.followers_ids, screen_name=user.screen_name, skip_cache_write=user.protected).items(limit=limit)

    def lookup_users(self, user_ids=None, screen_names=None, limit=2000, step=100):
        '''Converts ids/screen_names to full user objects using api calls.
        
        To avoid exhausting api quota, we only lookup 'limit' users.  The api
        lets us lookup 100 users at a time.
        '''
        if user_ids is None: user_ids = []
        if screen_names is None: screen_names = []
        
        try:
            len(user_ids)
        except TypeError:
            user_ids = list(user_ids)
        
        try:
            len(screen_names)
        except TypeError:
            screen_names = list(screen_names)
            
        users = []
        stop = min(len(user_ids), limit)
        for start in range(0, stop, step):
            try:
                users.extend(
                    self.api.lookup_users(user_ids=user_ids[start:start+step]))
            except Exception:
                pass

        stop = min(len(screen_names), limit)
        for start in range(0, stop, step):
            try:
                users.extend(
                    self.api.lookup_users(screen_names=screen_names[start:start+step]))
            except Exception:
                pass
        
        return users
    
    def get_statuses(self, users, limit=25):
        '''Gets statuses for users (annotated with followers_count of user)
        
        Params:
            users: list of users
            limit: maximum number of users to process
            
        Returns:
            List of (status, follower_count) tuples
        '''
        statuses = []
        for user in users[0:limit]:
            try:
                statuses.extend(zip(self.api.user_timeline(
                    screen_name=user.screen_name, count=10, include_rts=True,
                    include_entities=True, trim_user=True, skip_cache_write=user.protected),
                                    repeat(user.followers_count)))
            except tweepy.TweepError as e:
                print("TweepError: %s" % e)
        return statuses
    
    def detect_entities(self, statuses, limit = 100):
        '''Detects relevant mentions and hashtags in statuses
        
        Params:
            statuses: List of (status, followers_count) tuples
            limit: maximum number of mentions and hashtags to return
            
        Returns:
            (ranked mentioned-users, ranked hashtags), up to `limit` in length
        '''
        mentions = defaultdict(int)
        hashtags = defaultdict(int)
        for (status, follower_count) in statuses:
            for mention_ent in status.entities['user_mentions']:
                mention = mention_ent['screen_name']
                mentions[mention] += math.log(follower_count+1)
            for hashtag_ent in status.entities['hashtags']:
                hashtag = "#" + hashtag_ent['text']
                hashtags[hashtag] += math.log(follower_count+1)

        sorted_hashtags = sorted(hashtags, key=lambda key: hashtags[key], reverse=True)[0:limit]
        sorted_mentions = sorted(mentions, key=lambda key: mentions[key], reverse=True)[0:limit]
        mention_users = self.lookup_users(screen_names=sorted_mentions)
        sorted_mention_users = sorted(mention_users, key=lambda user: mentions[user.screen_name], reverse=True)
        
        return (sorted_mention_users, sorted_hashtags)                 
