from .exceptions import *

def rate_limit_check(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RateLimitError:
            return redirect('rate_limit')
    return wrapper
