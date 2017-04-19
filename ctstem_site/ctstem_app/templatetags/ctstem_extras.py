from django import template
from django.utils.encoding import force_unicode
from ctstem_app import models
import datetime

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
def get_curriculum_title(curriculum_id):
  try:
    if curriculum_id != 'None':
      title = models.Curriculum.objects.get(id=curriculum_id).title
      return title
    else:
      return None
  except models.Curriculum.DoesNotExist:
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
def getStudentInfo(value):
  student = models.Student.objects.get(id=value)
  return student

@register.filter
def iterate(value):
  return range(1, value+1)

@register.filter
def is_bookmarked(obj, qset):
  return obj in qset

@register.filter
def is_favorite(curriculum_id, teacher_id):
  return models.BookmarkedCurriculum.objects.all().filter(curriculum__id=curriculum_id, teacher__id=teacher_id).exists()

@register.filter
def getFeedback(response_id):
  feedback = models.QuestionFeedback.objects.all().filter(response__id=response_id)[0]
  return feedback.feedback

@register.filter
def get_item(dictionary, key):
  return dictionary.get(key)

@register.filter
def get_type(value):
  return type(value).__name__

@register.filter
def get_ascii_char(value):
  return [chr(i) for i in xrange(65,91)][int(value)]

@register.filter
def format_time(value):
  if value:
    time = datetime.timedelta(seconds=int(value))
    return str(time)
  else:
    return ''

@register.filter
def has_response(curriculum, user):
  if hasattr(user, 'administrator') == True or hasattr(user, 'researcher') == True:
    assignments = models.Assignment.objects.all().filter(curriculum__id = curriculum.id)
  elif hasattr(user, 'school_administrator') == True:
    assignments = models.Assignment.objects.all().filter(curriculum__id = curriculum.id, group__teacher__school = user.school_administrator.school)
  elif hasattr(user, 'teacher') == True:
    assignments = models.Assignment.objects.all().filter(curriculum__id = curriculum.id, group__teacher = user.teacher)
  else:
    return False

  instances = models.AssignmentInstance.objects.all().filter(assignment__in=assignments)
  if instances:
    return True
  else:
    return False

bulk_header = 'Select Bulk Action'

def StudentFilters(context):
    groups = context.get('groups')
    journals = context.get('journals')
    request = context.get('request')
    group_choices = [{'display':'All','query_string':'?','selected':request=={},}]
    for group in groups:
        group_choices.append({'display':group.title,'query_string':'?f=groups__in:'+str(group.id),'selected':request.get('f')=='groups__in:'+str(group.id),})
    group_choices.append({'display':'(none)','query_string':'?f=groups__isnull:True','selected':request.get('f')=='groups__isnull:True',})
    journal_choices = [{'display':'All','query_string':'?','selected':request=={},}]
    for journal in journals:
        journal_choices.append({'display':journal.title,'query_string':'?f=assignment__id__exact:'+str(journal.id),'selected':request.get('f')=='assignment__id__exact:'+str(journal.id),})
    journal_choices.append({'display':'(unassigned)','query_string':'?f=assignment__isnull:True','selected':request.get('f')=='assignment__isnull:True',})
    return [{'title':'Group','choices':group_choices},{'title':'Assignment','choices':journal_choices},]

@register.inclusion_tag("ctstem_app/admin/filter.html", takes_context=True)
def student_filters(context):

    return {'student_filters':StudentFilters(context)}

#################################################################################
# currently only using the following

def UserActions(context):
    return [{'description':bulk_header,'value':''},
        {'description':'Delete Selected Users','value':'delete_selected'},
        {'description':'Activate Selected Users','value':'activate_selected'},
        {'description':'Inactivate Selected Users','value':'inactivate_selected'},]

@register.inclusion_tag("ctstem_app/admin/actions.html", takes_context=True)
def user_actions(context):
    return {'actions':UserActions(context)}

def TeacherActions(context):
  actions = UserActions(context)
  actions.append({'description': 'Update School', 'value': 'school_selected'})
  return actions

@register.inclusion_tag("ctstem_app/admin/actions.html", takes_context=True)
def teacher_actions(context):
  return {'actions':TeacherActions(context)}

def StudentActions(context):
  actions = TeacherActions(context)
  actions.append({'description':'Update Parental Consent','value':'parental_consent_selected'})
  return actions

@register.inclusion_tag("ctstem_app/admin/actions.html", takes_context=True)
def student_actions(context):
    return {'actions':StudentActions(context)}

@register.filter
def get_student_groups(id):
  student = models.Student.objects.get(id=id)
  memberships = student.student_membership.all()
  return memberships

@register.filter
def get_teacher_groups(id):
  teacher = models.Teacher.objects.get(id=id)
  groups = teacher.groups.all()
  return groups
