from datetime import datetime
from django.conf import settings
from django.contrib import auth, messages
from ctstem_app import models
from ctstem_app.exceptions import GoogleLoginException
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django import shortcuts

class UpdateSession(MiddlewareMixin):

  def process_request(self, request):
    if not request.user.is_authenticated:
      #Can't log out if not logged in
      return
    # only update non ajax requests
    if not request.is_ajax():
      request.session['last_touch'] = str(datetime.now())

class CustomExceptionMiddleware(MiddlewareMixin):

  def process_exception(self, request, exception):

    if isinstance(exception, GoogleLoginException):
     messages.error(request, str(exception))

    return shortcuts.redirect('ctstem:home')

