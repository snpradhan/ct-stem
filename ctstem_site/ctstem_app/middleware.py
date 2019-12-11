from datetime import datetime
from django.conf import settings
from django.contrib import auth, messages
from ctstem_app import models
from django.utils.deprecation import MiddlewareMixin

class UpdateSession(MiddlewareMixin):

  def process_request(self, request):
    if not request.user.is_authenticated() :
      #Can't log out if not logged in
      return
    # only update non ajax requests
    if not request.is_ajax():
      request.session['last_touch'] = str(datetime.now())
