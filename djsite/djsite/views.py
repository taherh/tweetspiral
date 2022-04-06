import os
import socket, sys
from django.http import HttpResponse

def homepage(request):
    return HttpResponse("Hello!")