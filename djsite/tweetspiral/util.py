from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.shortcuts import redirect


from .exceptions import *

def error_check(func):
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except RateLimitError as e:
            print("Error: %r" % e)
            return redirect('rate_limit_error')
        except Exception as e:
            print("Error: %r" % e)
            if settings.LOGOUT_ON_ERROR:
                django_logout(request)
            if settings.DEBUG: raise
            return redirect('error')
    return wrapper
