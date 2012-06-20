from django.conf import settings
from django.shortcuts import redirect

from .exceptions import *

def error_check(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            print("Error: %r" % e)
            return redirect('rate_limit_error')
        except Exception as e:
            print("Error: %r" % e)
            if settings.DEBUG: raise
            return redirect('error')
    return wrapper
