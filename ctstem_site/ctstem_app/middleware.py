from datetime import datetime
from django.core.cache import cache
from django.conf import settings
from django.contrib import auth, messages
from ctstem_app import models
from ctstem_app.exceptions import GoogleLoginException
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django import shortcuts
from django.contrib.auth.models import User

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




ONLINE_THRESHOLD = getattr(settings, 'ONLINE_THRESHOLD', 60*15)

def get_online_now(self):
  return User.objects.filter(id__in=self.online_now_ids or [])

class OnlineNowMiddleware(MiddlewareMixin):
  """
  Maintains a list of users who have interacted with the website recently.
  Their user IDs are available as ``online_now_ids`` on the request object,
  and their corresponding users are available (lazily) as the
  ``online_now`` property on the request object.
  """


  def process_request(self, request):
    # First get the index
    uids = cache.get('online-now', [])

    # Perform the multiget on the individual online uid keys
    online_keys = ['online-%s' % (u,) for u in uids]
    fresh = cache.get_many(online_keys).keys()
    online_now_ids = [int(k.replace('online-', '')) for k in fresh]

    # If the user is authenticated, add their id to the list
    if request.user.is_authenticated():
        uid = request.user.id
        # If their uid is already in the list, we want to bump it
        # to the top, so we remove the earlier entry.
        if uid in online_now_ids:
            online_now_ids.remove(uid)
        online_now_ids.append(uid)

    # Attach our modifications to the request object
    request.__class__.online_now_ids = online_now_ids
    request.__class__.online_now = property(get_online_now)

    # Set the new cache
    cache.set('online-%s' % (request.user.pk,), True, ONLINE_THRESHOLD)
    cache.set('online-now', online_now_ids, ONLINE_THRESHOLD)
