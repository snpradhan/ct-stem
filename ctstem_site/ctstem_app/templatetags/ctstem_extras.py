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

@register.filter
def get_curriculum_question(question_id):
  try:
    if question_id != 'None':
      question = models.Question.objects.get(curriculum_question__id=question_id)
      return question
    else:
      return None
  except models.Question.DoesNotExist:
    return None

@register.filter
def is_in(var, obj):
    return var in obj


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

@register.filter(name='splitlines')
def split(value):
    return value.splitlines()

@register.filter
def format_iframe(html_string):
    return html_string.replace('<iframe', '<tr><td id="lessonContent"><p><iframe').replace('</iframe>', '</iframe></p></td></tr>')

@register.filter
def inline_style(html_string):
  return html_string.replace('<li', '<li style="margin:0;padding:0"');

@register.filter
def getSelectedTaxonomy(form, field):
  selectedTaxonomy = [value for value, label in form.fields[field].choices if value in form[field].value()]
  taxonomies = models.Subcategory.objects.all().filter(id__in=selectedTaxonomy)
  return taxonomyHelper(taxonomies)

@register.filter
def taxonomyHelper(taxonomies):
  taxonomy_dictionary = {}
  for taxonomy in taxonomies:
    if taxonomy.category.standard.name in taxonomy_dictionary:
      if taxonomy.category.name in taxonomy_dictionary[taxonomy.category.standard.name]:
        taxonomy_dictionary[taxonomy.category.standard.name][taxonomy.category.name].append(taxonomy)
      else:
        taxonomy_dictionary[taxonomy.category.standard.name][taxonomy.category.name] = [taxonomy]
    else:
      taxonomy_dictionary[taxonomy.category.standard.name] = {taxonomy.category.name: [taxonomy]}

  return taxonomy_dictionary.items()

@register.filter
def getTaxonomy(value):
  taxonomy = models.Subcategory.objects.get(id=value)
  return taxonomy

@register.filter
def iterate(value):
  return range(1, value+1)

@register.filter
def is_bookmarked(obj, qset):
  return obj in qset

@register.filter
def getFeedback(response_id):
  feedback = models.QuestionFeedback.objects.all().filter(response__id=response_id)[0]
  return feedback.feedback
