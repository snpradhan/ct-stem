from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaultfilters import stringfilter
import json
import datetime
import re
import random

register = template.Library()

@register.simple_tag
def navactive(request, urls, args=None):
  if args:
    if request.path in ( reverse(url, args=(args,)) for url in urls.split() ):
      return "active"
  else:
    if request.path in ( reverse(url) for url in urls.split() ):
      return "active"
  return ""


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")
