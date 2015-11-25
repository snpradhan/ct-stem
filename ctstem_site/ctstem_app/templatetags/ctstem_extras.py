from django import template
from django.utils.encoding import force_unicode
from ctstem_app import models

register = template.Library()

@register.filter
def selected_labels(form, field):
    return [label for value, label in form.fields[field].choices if value in form[field].value()]

@register.filter
def selected_question(question_id):
  try:
    if question_id != 'None':
      question = models.Question.objects.get(id=question_id)
      return question.question_text
    else:
      return ''
  except models.Question.DoesNotExist:
    return ''

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

@register.filter(name='split')
def split(value, arg):
    return value.split(arg)


@register.filter
def format_iframe(html_string):
    return html_string.replace('<iframe', '<tr><td id="lessonContent"><p><iframe').replace('</iframe>', '</iframe></p></td></tr>')

@register.filter
def inline_style(html_string):
  return html_string.replace('<li', '<li style="margin:0;padding:0"');
