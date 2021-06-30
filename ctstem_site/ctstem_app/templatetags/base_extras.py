from django import template
from django.conf import settings
from django.urls import reverse
from django.template.defaultfilters import stringfilter
import json
import datetime
import re
import random
import os
import posixpath
import stat
import urllib.request, urllib.parse, urllib.error
from django.contrib.staticfiles import finders

register = template.Library()

@register.simple_tag
def navactive(request, urls, *args):
  if args:
   if request.path in ( reverse(url, args=args) for url in urls.split() ):
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
    normalized_path = posixpath.normpath(urllib.parse.unquote(path)).lstrip('/')
    absolute_path = finders.find(normalized_path)
    if not absolute_path and getattr(settings, 'STATIC_ROOT', None):
        absolute_path = os.path.join(settings.STATIC_ROOT, path)
    if absolute_path:
        return '%s%s?v=%s' % (settings.STATIC_URL, path, os.stat(absolute_path)[stat.ST_MTIME])
    return path

@register.filter
def get_unique_messages(msg):
  unique_message_texts = []
  unique_message_objects = []
  for m in msg:
    if m.message not in unique_message_texts:
      unique_message_texts.append(m.message)
      unique_message_objects.append(m)
  return unique_message_objects
