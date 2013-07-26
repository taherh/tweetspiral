# Here is the template for the local_settings.py file
# Rename this file to local_settings.py and fill in your appropriate passwords and secret keys
# The actual version of this file should not be checked into a shared git repo

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.   
        'NAME': 'django_db',                      # Or path to database file if using sqlite3.                             
        'USER': 'django',                      # Not used with sqlite3.                                                    
        'PASSWORD': 'PASSWORD',                  # Not used with sqlite3.                                                
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.                       
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.                         
    }
}

API_CACHE = 'redis'  # 'memory', 'file', or 'redis'
API_FILE_CACHE_PATH = '/srv/cache/tweepy/'
API_CACHE_TIMEOUT = 259200  # 4 days

SECRET_KEY = ''

# The consumer keys can be found on your application's Details                                                             
# page located at https://dev.twitter.com/apps (under "OAuth settings")                                                    
TWITTER_CONSUMER_KEY=""
TWITTER_CONSUMER_SECRET=""
# You can generate a bearer token using https://github.com/taherh/twitter_application_auth
TWITTER_BEARER_TOKEN=""
