from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaultfilters import stringfilter
import json
import datetime
import re
import random
import os
import posixpath
import stat
import urllib
from django.contrib.staticfiles import finders

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


@register.simple_tag
def staticfile(path):
    normalized_path = posixpath.normpath(urllib.unquote(path)).lstrip('/')
    absolute_path = finders.find(normalized_path)
    if not absolute_path and getattr(settings, 'STATIC_ROOT', None):
        absolute_path = os.path.join(settings.STATIC_ROOT, path)
    if absolute_path:
        return '%s%s?v=%s' % (settings.STATIC_URL, path, os.stat(absolute_path)[stat.ST_MTIME])
    return path
