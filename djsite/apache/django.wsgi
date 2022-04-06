import os
import sys

path = '/srv/web/tweetspiral.com/djsite'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djsite.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
