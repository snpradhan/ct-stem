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

@register.filter(name='sort')
def listsort(value):
  if isinstance(value,dict):
    new_dict = SortedDict()
    key_list = value.keys()
    key_list.sort()
    for key in key_list:
      new_dict[key] = value[key]
    return new_dict
  elif isinstance(value, list):
    new_list = list(value)
    new_list.sort()
    return new_list
  else:
    return value
listsort.is_safe = True
