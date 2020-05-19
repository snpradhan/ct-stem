from django import template
from ctstem_app import models, views
from django.contrib import messages
import datetime
from django.db.models import Q
from django.utils import timezone
from collections import OrderedDict

register = template.Library()

@register.filter
def get_authors(queryset):
  return queryset.filter(privilege='E')

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

@register.simple_tag(takes_context=True)
def replace_iframe_tag(context, text):
  request = context.get('request')
  revised_text = views.replace_iframe_tag(request, text)
  return revised_text

@register.filter
def get_question(curriculum_question_id):
  try:
    if curriculum_question_id != 'None':
      question = models.Question.objects.get(curriculum_question__id=curriculum_question_id)
      return question
    else:
      return None
  except models.Question.DoesNotExist:
    return None

@register.filter
def get_curriculum_question(curriculum_question_id):
  try:
    if curriculum_question_id != 'None':
      curriculum_question = models.CurriculumQuestion.objects.get(id=curriculum_question_id)
      return curriculum_question
    else:
      return None
  except models.CurriculumQuestion.DoesNotExist:
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
def get_curriculum_object(curriculum_id):
  try:
    if curriculum_id != 'None':
      return models.Curriculum.objects.get(id=curriculum_id)
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
    new_dict = OrderedDict()
    key_list = list(value.keys())
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

  return list(taxonomy_dictionary.items())

@register.filter
def getTaxonomy(value):
  taxonomy = models.Subcategory.objects.get(id=value)
  return taxonomy

@register.filter
def getStandards(taxonomies):
  standards = []
  for taxonomy in taxonomies:
    if taxonomy.category.standard not in standards:
      standards.append(taxonomy.category.standard)
  return standards

@register.filter
def getStudentInfo(value):
  student = models.Student.objects.get(id=value)
  return student

@register.filter
def getTeacherInfo(value):
  teacher = models.Teacher.objects.get(id=value)
  return teacher

@register.filter
def getUserInfo(value):
  user = models.User.objects.get(id=value)
  return user

@register.filter
def iterate(value):
  return list(range(1, value+1))

@register.filter
def is_bookmarked(curriculum, teacher):
  bookmark = models.BookmarkedCurriculum.objects.all().filter(curriculum=curriculum, teacher=teacher).count()
  if bookmark:
    return True
  return False

@register.filter
def is_favorite(curriculum_id, teacher_id):
  return models.BookmarkedCurriculum.objects.all().filter(curriculum__id=curriculum_id, teacher__id=teacher_id).exists()

@register.filter
def getFeedback(response_id):
  feedback_queryset = models.QuestionFeedback.objects.all().filter(response__id=response_id)
  if feedback_queryset:
    return feedback_queryset[0].feedback
  else:
    return None

@register.filter
def get_item(dictionary, key):
  return dictionary.get(key)

@register.filter
def get_type(value):
  return type(value).__name__

@register.filter
def get_ascii_char(value):
  return [chr(i) for i in range(65,91)][int(value)]

@register.filter
def format_time(value):
  if value:
    time = datetime.timedelta(seconds=int(value))
    return str(time)
  else:
    return ''

@register.filter
def has_response(curriculum, user):
  if curriculum.curriculum_type != 'U':
    curricula = models.Curriculum.objects.all().filter(id=curriculum.id)
  else:
    curricula = curriculum.underlying_curriculum.all()

  if hasattr(user, 'administrator') == True or hasattr(user, 'researcher') == True:
    assignments = models.Assignment.objects.all().filter(curriculum__in=curricula)
  elif hasattr(user, 'school_administrator') == True:
    assignments = models.Assignment.objects.all().filter(curriculum__in=curricula, group__teacher__school=user.school_administrator.school)
  elif hasattr(user, 'teacher') == True:
    assignments = models.Assignment.objects.all().filter(Q(curriculum__in=curricula), Q(group__teacher=user.teacher) | Q(group__shared_with=user.teacher))
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
  return actions

@register.inclusion_tag("ctstem_app/admin/actions.html", takes_context=True)
def student_actions(context):
    return {'actions':StudentActions(context)}

def StudentInGroupAdminActions(context):
  actions = StudentActions(context)
  actions.append({'description':'Remove Selected Students From Class','value':'remove_selected'})
  return actions

@register.inclusion_tag("ctstem_app/admin/actions.html", takes_context=True)
def student_in_group_admin_actions(context):
    return {'actions':StudentInGroupAdminActions(context)}

def StudentInGroupTeacherActions(context):
  actions = UserActions(context)
  actions.append({'description':'Remove Selected Students From Class','value':'remove_selected'})
  return actions

@register.inclusion_tag("ctstem_app/admin/actions.html", takes_context=True)
def student_in_group_teacher_actions(context):
    return {'actions':StudentInGroupTeacherActions(context)}

def GroupActions(context):
    return [{'description':bulk_header,'value':''},
        {'description':'Activate Selected Classes','value':'activate_selected'},
        {'description':'Inactivate Selected Classes','value':'inactivate_selected'},]

@register.inclusion_tag("ctstem_app/admin/actions.html", takes_context=True)
def group_actions(context):
    return {'actions':GroupActions(context)}

@register.filter
def get_student_groups(id):
  student = models.Student.objects.get(id=id)
  memberships = student.student_membership.all().filter(group__is_active=True)
  return memberships

@register.filter
def get_teacher_groups(id):
  teacher = models.Teacher.objects.get(id=id)
  groups = teacher.groups.all().filter(is_active=True)
  return groups

@register.simple_tag(takes_context=True)
def get_underlying_curriculum(context, curriculum_id):
  request = context.get('request')
  curriculum = models.Curriculum.objects.get(id=curriculum_id)
  if curriculum.status != 'R':
    action = 'preview'
  else:
    action = 'restore'
  underlying_curriculum = views.underlyingCurriculum(request, action, curriculum_id)
  list(messages.get_messages(request))
  return underlying_curriculum

# get the next lesson in the sequence for an underlying lesson
@register.filter
def get_next_curriculum(curriculum_id):
  curriculum = models.Curriculum.objects.get(id=curriculum_id)
  next_curriculum = models.Curriculum.objects.all().filter(unit=curriculum.unit, order=curriculum.order+1)
  if len(next_curriculum) > 0:
    return next_curriculum[0]
  else:
    return None

# get the previous lesson in the sequence for an underlying lesson
@register.filter
def get_previous_curriculum(curriculum_id):
  curriculum = models.Curriculum.objects.get(id=curriculum_id)
  previous_curriculum = models.Curriculum.objects.all().filter(unit=curriculum.unit, order=curriculum.order-1)
  if len(previous_curriculum) > 0:
    return previous_curriculum[0]
  else:
    return None

@register.filter
def get_curriculum_count(queryset, status):
  return queryset.filter(status=status).count()

@register.filter
def get_referenced_questions(step, instance=False):
  step_order = step.order
  curriculum = step.curriculum
  curriculum_questions = models.CurriculumQuestion.objects.all().filter(step__in=curriculum.steps.all(), referenced_by__isnull=False, step__order__lt=step_order).order_by('step__order', 'order')
  referenced_question = []
  for curr_question in curriculum_questions:
    if curr_question.referenced_by:
      referenced_by = list(map(int, curr_question.referenced_by.split(',')))
      if step_order in referenced_by:
        if instance:
          #get the response for the question
          response = models.QuestionResponse.objects.get(curriculum_question=curr_question, step_response__instance=instance)
          referenced_question.append((curr_question, response))
        else:
          referenced_question.append(curr_question)

  if referenced_question:
    return referenced_question
  else:
    return False

@register.filter
def date_has_past(dt):
  return dt < timezone.now()

@register.filter
def get_class_assignment_status(assignment_id):
  assignment = models.Assignment.objects.get(id=assignment_id)
  assignment_instances = models.AssignmentInstance.objects.all().filter(assignment__id=assignment_id)
  status = 'N'
  for instance in assignment_instances:
    if instance.status != 'N':
      status = instance.status
      break

  return status

@register.filter
def subtract(value, arg):
  return value - arg

@register.filter
def class_last_login(group):
  memberships = models.Membership.objects.all().filter(group=group)
  last_login = None
  for membership in memberships:
    login = membership.student.user.last_login
    if last_login is None and login is not None:
      last_login = login
    elif last_login is not None and login is not None and login > last_login:
      last_login = login

  return last_login

@register.filter
def is_teacher_authored(curriculum):
  authors = models.CurriculumCollaborator.objects.all().filter(curriculum=curriculum, privilege='E')
  for author in authors:
    if hasattr(author.user, 'teacher'):
      return True

  return False

@register.simple_tag(takes_context=True)
def check_curriculum_permission(context, curriculum_id, action):
  request = context.get('request')
  has_permission = views.check_curriculum_permission(request, curriculum_id, action)

  list(messages.get_messages(request))
  return has_permission

@register.simple_tag(takes_context=True)
def get_curriculum_locked_by(context, curriculum_id):
  request = context.get('request')
  locked_by = views.get_curriculum_locked_by(request, curriculum_id)
  return locked_by

@register.filter
def get_page_start_index(paginator, page_number):
  return paginator.page(page_number).start_index()

@register.filter
def get_page_end_index(paginator, page_number):
  return paginator.page(page_number).end_index()

@register.filter
def get_collaborator_privilege_display(privilege_value):
  privilege_display = dict(models.CURRICULUM_PRIVILEGE_CHOICES)[privilege_value]
  return privilege_display

@register.assignment_tag(takes_context=True)
def is_my_curriculum(context, curriculum):
  request = context.get('request')
  is_author = False
  if request.user.is_authenticated:
    author_count = models.CurriculumCollaborator.objects.all().filter(curriculum=curriculum, user=request.user, privilege='E').count()

    if author_count == 1:
      if hasattr(request.user, 'teacher') or hasattr(request.user, 'researcher'):
        is_author = True

  return is_author

@register.assignment_tag(takes_context=True)
def is_curriculum_shared_with_me(context, curriculum):
  request = context.get('request')
  return views.is_curriculum_shared_with_me(request, curriculum.id)

@register.assignment_tag(takes_context=True)
def is_curriculum_assigned(context, curriculum):
  request = context.get('request')
  return views.is_curriculum_assigned(request, curriculum.id)

@register.assignment_tag(takes_context=True)
def is_curriculum_assigned_by_me(context, curriculum):
  request = context.get('request')
  return views.is_curriculum_assigned_by_me(request, curriculum.id)
