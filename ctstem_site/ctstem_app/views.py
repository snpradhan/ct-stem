from ctstem_app import models, forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models.functions import Lower
from django import http, shortcuts, template
from django.shortcuts import render, render_to_response
from django.contrib import auth, messages
from django.forms.models import inlineformset_factory, modelformset_factory
from nested_formset import nestedformset_factory
from slugify import slugify
import json
from django_xhtml2pdf.utils import render_to_pdf_response
from django.template.loader import render_to_string, get_template
from django.template import Context
import io as StringIO
import xhtml2pdf.pisa as pisa
import os
from django.conf import settings
import datetime
from django.utils.crypto import get_random_string
import string
import csv
import xlwt
from django.db.models import Q
from django.core.files.base import ContentFile
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.models import Site
from django.core import serializers
import zipfile
from django.core.files import File
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse
from urllib.request import urlretrieve
import base64
from django.utils.encoding import smart_str
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.db.models import Max, Min
import logging
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from dal import autocomplete
from django.core.cache import cache
import re

logger = logging.getLogger('django')

####################################
# HOME
####################################
def home(request):
  #get published lessons
  if hasattr(request.user, 'student') == True:
    return shortcuts.redirect('ctstem:assignments', bucket='inbox')
  else:
    curr_type = ['U', 'L']
    curricula = models.Curriculum.objects.all().filter(status='P', unit__isnull=True, curriculum_type__in=curr_type, feature_rank__isnull=False).order_by('feature_rank')[:4]
    if request.user.is_authenticated:
      if hasattr(request.user, 'administrator'):
        school = None
        requester_role = ''
      elif hasattr(request.user, 'researcher'):
        school = None
        requester_role = 'R'
      elif hasattr(request.user, 'teacher'):
        school = request.user.teacher.school
        requester_role = 'T'
      else:
        school = None
        requester_role = ''

    if request.method == 'GET':
      redirect_url = request.GET.get('next', '')
      target = None
      if 'register' in redirect_url:
        target = '#register'
      elif 'validate' in redirect_url:
        target = '#validate'
      elif 'password_reset' in redirect_url:
        target = '#password'
      elif 'login' in redirect_url:
        target ='#login'

      if target and request.user.is_authenticated:
        logout(request)

      context = {'curricula': curricula, 'redirect_url': redirect_url, 'target': target}
      return render(request, 'ctstem_app/Home.html', context)

    return http.HttpResponseNotAllowed(['GET'])

def send_email(subject, message, sender, to_list):
    msg = EmailMessage(subject, message, sender, to_list)
    msg.content_subtype = "html"  # Main content is now text/html
    return msg.send()

####################################
# ABOUT US
####################################
def team(request):
  current_members = models.Team.objects.all().filter(current=True).order_by('order')
  past_members = models.Team.objects.all().filter(current=False).order_by('order')
  context = {'current_members': current_members, 'past_members': past_members}
  return render(request, 'ctstem_app/Team.html', context)

####################################
# Curricula TABLE VIEW
####################################
@login_required
def curricula(request, bucket='unit', status='public'):

  curriculum_type = []
  if bucket == 'unit':
    curriculum_type = ['U']
  elif bucket == 'lesson':
    curriculum_type = ['L']
  elif bucket == 'assessment':
    curriculum_type = ['A']
  elif bucket in ['teacher_authored', 'my', 'favorite', 'shared', 'deleted']:
    curriculum_type = ['U', 'L', 'A']

  stat = []
  curricula = models.Curriculum.objects.extra(select={'modified_year': 'EXTRACT(YEAR FROM modified_date)',
                          'modified_month': 'EXTRACT(MONTH FROM modified_date)',
                          'modified_day': 'EXTRACT(DAY FROM modified_date)'})
  if bucket in ['unit', 'lesson', 'assessment']:
    if hasattr(request.user, 'administrator') or hasattr(request.user, 'author'):
      if status == 'archived':
        stat = ['A']
      elif status == 'private':
        stat = ['D']
      else:
        stat = ['P']
    else:
      stat = ['P']
    curricula = curricula.filter(unit__isnull=True, curriculum_type__in = curriculum_type, status__in = stat)

  elif bucket == 'teacher_authored' and (hasattr(request.user, 'administrator') or hasattr(request.user, 'author')):
    stat = ['D', 'P', 'A']
    curricula = curricula.filter(unit__isnull=True, curriculum_type__in = curriculum_type, status__in = stat, curriculumcollaborator__user__teacher__isnull=False, curriculumcollaborator__privilege='E').distinct()
  elif bucket == 'deleted' and hasattr(request.user, 'administrator'):
    stat = ['R']
    deleted_lessons = curricula.filter(unit__isnull=False, curriculum_type__in = ['L', 'A'], status__in = stat).distinct()
    deleted_lessons_units = deleted_lessons.values_list('unit', flat=True)
    curricula = curricula.filter(Q(unit__isnull=True), Q(curriculum_type__in = curriculum_type), Q(status__in = stat) | Q(id__in=deleted_lessons_units)).distinct()

  elif bucket == 'my' and (hasattr(request.user, 'teacher') or hasattr(request.user, 'researcher')):
    stat = ['D', 'P', 'A']
    curricula = curricula.filter(unit__isnull=True, curriculum_type__in = curriculum_type, status__in = stat, curriculumcollaborator__user=request.user, curriculumcollaborator__privilege='E')
  elif bucket == 'favorite' and hasattr(request.user, 'teacher'):
    stat = ['D', 'P', 'A']
    curricula = curricula.filter(Q(unit__isnull=True), Q(curriculum_type__in=curriculum_type), Q(bookmarked__teacher=request.user.teacher), Q(status__in=stat) | (Q(curriculumcollaborator__user=request.user) & Q(curriculumcollaborator__privilege='V'))).distinct()
  elif bucket == 'shared' and (hasattr(request.user, 'teacher') or hasattr(request.user, 'researcher')):
    stat = ['D', 'P', 'A']
    shared_lessons = curricula.filter(unit__isnull=False, curriculum_type__in = 'L', status__in = stat, curriculumcollaborator__user=request.user, curriculumcollaborator__privilege='V').distinct()
    shared_lessons_units = shared_lessons.values_list('unit', flat=True)
    curricula = curricula.filter(Q(unit__isnull=True), Q(curriculum_type__in = curriculum_type), Q(status__in = stat), (Q(curriculumcollaborator__user=request.user) & Q(curriculumcollaborator__privilege='V')) | Q(id__in=shared_lessons_units)).distinct()
  else:
    curricula = None
    messages.error(request, "There are no curricula for the requested category.")

  if curricula:
    #search
    search_criteria = None
    if request.method == 'POST':
      data = request.POST.copy()
      if 'search_criteria' in data:
        search_criteria = data['search_criteria']
      searchForm = forms.SearchForm(data)
    else:
      searchForm = forms.SearchForm()

    if search_criteria:
      curricula = searchCurricula(request, curricula, search_criteria)

    sort_order = [{'order_by': 'feature_rank', 'direction': 'asc', 'ignorecase': 'false'},
                  {'order_by': 'modified_year', 'direction': 'desc', 'ignorecase': 'false'},
                  {'order_by': 'modified_month', 'direction': 'desc', 'ignorecase': 'false'},
                  {'order_by': 'modified_day', 'direction': 'desc', 'ignorecase': 'false'},
                  {'order_by': 'title', 'direction': 'asc', 'ignorecase': 'true'}]
    curricula_list = paginate(request, curricula, sort_order, 25)
  else:
    curricula_list = None
    searchForm = forms.SearchForm()
  #if curricula:
  #  curricula = curricula.order_by('-modified_date', Lower('title'))
  context = {'curricula': curricula_list, 'bucket': bucket, 'status': status, 'searchForm': searchForm}
  return render(request, 'ctstem_app/Curricula.html', context)

####################################
# Curricula Tile VIEW
####################################
def curriculatiles(request):

  if request.method == 'GET' or request.method == 'POST':
    curricula = models.Curriculum.objects.extra(select={'modified_year': 'EXTRACT(YEAR FROM modified_date)',
                          'modified_month': 'EXTRACT(MONTH FROM modified_date)',
                          'modified_day': 'EXTRACT(DAY FROM modified_date)',
                          'is_active': "status <> 'R' and status <> 'A'",
                          'bookmark_count': 'SELECT COUNT(*) FROM ctstem_app_bookmarkedcurriculum WHERE ctstem_app_bookmarkedcurriculum.curriculum_id = ctstem_app_curriculum.id'})

    search_criteria = None
    if request.method == 'GET':
      initial = None
      if 'bucket' in request.GET:
        initial = {'buckets': [request.GET['bucket']]}
      searchForm = forms.CurriculaSearchForm(user=request.user, initial=initial)

    elif request.method == 'POST':
      data = request.POST.copy()
      searchForm = forms.CurriculaSearchForm(user=request.user, data=data)
      search_criteria = eval(json.dumps(dict(data.lists())))

    curricula = searchCurriculaTiles(request, curricula, search_criteria)

    sort_order = None
    if search_criteria and 'sort_by' in search_criteria and search_criteria['sort_by'][0] != '':
      #sort by modified date
      if search_criteria['sort_by'][0] == 'D':
        sort_order = [{'order_by': 'is_active', 'direction': 'desc', 'ignorecase': 'false'},
                      {'order_by': 'modified_year', 'direction': 'desc', 'ignorecase': 'false'},
                      {'order_by': 'modified_month', 'direction': 'desc', 'ignorecase': 'false'},
                      {'order_by': 'modified_day', 'direction': 'desc', 'ignorecase': 'false'}]
      #sort by title alphabetically
      elif search_criteria['sort_by'][0] == 'A':
        sort_order = [{'order_by': 'is_active', 'direction': 'desc', 'ignorecase': 'false'},
                      {'order_by': 'title', 'direction': 'asc', 'ignorecase': 'true'}]
      #sort by popularity
      elif search_criteria['sort_by'][0] == 'P':
        sort_order = [{'order_by': 'is_active', 'direction': 'desc', 'ignorecase': 'false'},
                      {'order_by': 'bookmark_count', 'direction': 'desc', 'ignorecase': 'false'}]
    else:
      sort_order = [{'order_by': 'is_active', 'direction': 'desc', 'ignorecase': 'false'},
                    {'order_by': 'feature_rank', 'direction': 'asc', 'ignorecase': 'false'},
                    {'order_by': 'modified_year', 'direction': 'desc', 'ignorecase': 'false'},
                    {'order_by': 'modified_month', 'direction': 'desc', 'ignorecase': 'false'},
                    {'order_by': 'modified_day', 'direction': 'desc', 'ignorecase': 'false'},
                    {'order_by': 'title', 'direction': 'asc', 'ignorecase': 'true'}]

    curricula_list = paginate(request, curricula, sort_order, 12)
    context = {'curricula': curricula_list, 'searchForm': searchForm }

    template = 'ctstem_app/CurriculaTiles.html'
    if request.is_ajax():
      template = 'ctstem_app/CurriculaTilesPaging.html'
      context['parent'] = 'curricula'

    return render(request, template, context)
    #return render_to_response(template, context, context_instance=RequestContext(request))
  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# CREATE MODIFY a curriculum
####################################
def curriculum(request, id=''):
  try:
    unit_id = None
    # curriculum exists
    if '' != id:
      has_permission = check_curriculum_permission(request, id, 'modify')
      if has_permission:
        curriculum = models.Curriculum.objects.get(id=id)
        if curriculum.curriculum_type == 'U':
          unit_id = curriculum.id
        elif curriculum.unit:
          unit_id = curriculum.unit.id
      else:
        if request.META.get('HTTP_REFERER'):
          if 'login' in request.META.get('HTTP_REFERER'):
            return shortcuts.redirect('ctstem:home')
          else:
            return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
          return shortcuts.redirect('ctstem:home')
    #curriculum does not exist
    else:
      has_permission = check_curriculum_permission(request, id, 'create')
      if has_permission:
        if 'unit_id' in request.GET:
          unit_id = request.GET['unit_id']
          unit = models.Curriculum.objects.get(id=unit_id)
          curriculum = models.Curriculum(curriculum_type='L', unit=unit)
        else:
          curriculum = models.Curriculum()
      else:
         return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    newQuestionForm = forms.QuestionForm()

    if request.method == 'GET':
      initial_collaborator_data = []
      if '' == id:
        initial_collaborator_data = [{'user': request.user, 'ORDER': 1, 'privilege': 'E'}]
      form = forms.CurriculumForm(user=request.user, instance=curriculum, prefix='curriculum')
      #AssessmentStepFormSet = inlineformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,can_delete=True, can_order=True, extra=1)
      CollaboratorFormSet = inlineformset_factory(models.Curriculum, models.CurriculumCollaborator, form=forms.CurriculumCollaboratorForm, formset=forms.CollaboratorInlineFormSet, can_delete=True, can_order=True, extra=len(initial_collaborator_data)+1)

      StepFormSet = nestedformset_factory(models.Curriculum, models.Step, form=forms.StepForm,
                                                    nested_formset=inlineformset_factory(models.Step, models.CurriculumQuestion, form=forms.CurriculumQuestionForm, can_delete=True, can_order=True, extra=1),
                                                    can_delete=True, can_order=True, extra=1)
      AttachmentFormSet = inlineformset_factory(models.Curriculum, models.Attachment, form=forms.AttachmentForm, can_delete=True, can_order=True, extra=1)

      formset = StepFormSet(instance=curriculum, prefix='form')
      collaborator_formset = CollaboratorFormSet(instance=curriculum, prefix='collaborator_form')

      if initial_collaborator_data:
        for subform, collaborator_data in zip(collaborator_formset.forms, initial_collaborator_data):
          subform.initial = collaborator_data

      teacher_attachment_formset = AttachmentFormSet(instance=curriculum, prefix='teacher_attachment_form', queryset=models.Attachment.objects.filter(teacher_only=True))
      student_attachment_formset = AttachmentFormSet(instance=curriculum, prefix='student_attachment_form', queryset=models.Attachment.objects.filter(teacher_only=False))

      storage = messages.get_messages(request)
      modal_messages = []
      for message in storage:
        if message.extra_tags == 'modal_message':
          modal_messages.append(message)

      context = {'form': form, 'teacher_attachment_formset': teacher_attachment_formset, 'student_attachment_formset': student_attachment_formset, 'collaborator_formset': collaborator_formset, 'formset':formset, 'newQuestionForm': newQuestionForm, 'modal_messages': modal_messages, 'unit_id': unit_id }

      return render(request, 'ctstem_app/Curriculum.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      preview = data['preview']

      form = forms.CurriculumForm(user=request.user, data=data, files=request.FILES, instance=curriculum, prefix="curriculum")
      #AssessmentStepFormSet = inlineformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,
      CollaboratorFormSet = inlineformset_factory(models.Curriculum, models.CurriculumCollaborator, form=forms.CurriculumCollaboratorForm, formset=forms.CollaboratorInlineFormSet, can_delete=True, can_order=True, extra=1)
      StepFormSet = nestedformset_factory(models.Curriculum, models.Step, form=forms.StepForm,
                                                    nested_formset=inlineformset_factory(models.Step, models.CurriculumQuestion, form=forms.CurriculumQuestionForm, can_delete=True, can_order=True, extra=1),
                                                    can_delete=True, can_order=True, extra=1)

      AttachmentFormSet = inlineformset_factory(models.Curriculum, models.Attachment, form=forms.AttachmentForm, can_delete=True, can_order=True, extra=1)

      formset = StepFormSet(data, instance=curriculum, prefix='form')
      collaborator_formset = CollaboratorFormSet(data, instance=curriculum, prefix='collaborator_form')

      teacher_attachment_formset = AttachmentFormSet(data, request.FILES, instance=curriculum, prefix='teacher_attachment_form', queryset=models.Attachment.objects.filter(teacher_only=True))
      student_attachment_formset = AttachmentFormSet(data, request.FILES, instance=curriculum, prefix='student_attachment_form', queryset=models.Attachment.objects.filter(teacher_only=False))

      if form.is_valid() and formset.is_valid() and collaborator_formset.is_valid() and teacher_attachment_formset.is_valid() and student_attachment_formset.is_valid():
        savedCurriculum = form.save()

        #make sure curriculum order is present and unique in a unit
        if savedCurriculum.curriculum_type != 'U' and savedCurriculum.unit:
          reorder_underlying_curricula(request, savedCurriculum.unit.id)

        #only save collaborators for unit and stand alone lessons/assessments
        if not savedCurriculum.unit:
          collaborator_formset.save(commit=False)
          for collaboratorform in collaborator_formset.ordered_forms:
            collaboratorform.instance.order = collaboratorform.cleaned_data['ORDER']
            collaboratorform.instance.save()
          for obj in collaborator_formset.deleted_objects:
            obj.delete()


        teacher_attachment_formset.save(commit=False)
        for attachment_form in teacher_attachment_formset.ordered_forms:
          attachment_form.instance.teacher_only = True
          attachment_form.instance.save()
        for obj in teacher_attachment_formset.deleted_objects:
          obj.delete()

        student_attachment_formset.save(commit=False)
        for attachment_form in student_attachment_formset.ordered_forms:
          attachment_form.instance.teacher_only = False
          attachment_form.instance.save()
        for obj in student_attachment_formset.deleted_objects:
          obj.delete()

        formset.save(commit=False)
        for stepform in formset.ordered_forms:
          stepform.instance.order = stepform.cleaned_data['ORDER']
          stepform.instance.curriculum = savedCurriculum
          stepform.instance.save()
          for qform in stepform.nested.ordered_forms:
            qform.instance.order = qform.cleaned_data['ORDER']
            qform.instance.step = stepform.instance
            qform.instance.save()
          for obj in stepform.nested.deleted_objects:
            obj.delete()
        #remove deleted questions
        for obj in formset.deleted_objects:
          obj.delete()

        if request.is_ajax():
          response_data = {'status': 1, 'message': 'Curriculum Saved.'}
          return http.HttpResponse(json.dumps(response_data), content_type = 'application/json')
        else:
          #check which submit button was clicked and redirect accordingly
          messages.success(request, "Curriculum Saved.")
          if preview == '1':
            return shortcuts.redirect('ctstem:previewCurriculum', id=savedCurriculum.id)
          else:
            return shortcuts.redirect('/curriculum/%s' % savedCurriculum.id)
      else:
        print('form.errors', form.errors)
        print('formset.errors', formset.errors)
        print('teacher_attachment_formset.errors', teacher_attachment_formset.errors)
        print('student_attachment_formset.errors', student_attachment_formset.errors)
        print('collaborator_formset.errors', collaborator_formset.errors)
        print('collaborator_formset._non_form_errors', collaborator_formset._non_form_errors)
        if request.is_ajax():
          response_data = {'status': 0, 'message': 'The preview could not be generated because some mandatory fields are missing.  Please manually save the curriculum to see specific errors.'}
          return http.HttpResponse(json.dumps(response_data), content_type = 'application/json')
        else:
          #check which submit button was clicked and display error message accordingly
          if preview == '1':
            messages.error(request, "The preview could not be generated because some mandatory fields are missing.")
          else:
            messages.error(request, "The curriculum could not be saved because there were errors.  Please check the errors below.")
          context = {'form': form, 'teacher_attachment_formset': teacher_attachment_formset, 'student_attachment_formset': student_attachment_formset, 'collaborator_formset': collaborator_formset, 'formset':formset, 'newQuestionForm': newQuestionForm, 'unit_id': unit_id }
          return render(request, 'ctstem_app/Curriculum.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested curriculum not found</h1>')

####################################
# PREVIEW A Curriculum Activity page
####################################
def previewCurriculumActivity(request, id='', step_order=0):
  try:
    # check curriculum permission
    has_permission = check_curriculum_permission(request, id, 'preview')
    if has_permission:
      curriculum = models.Curriculum.objects.get(id=id)
    else:
      if request.META.get('HTTP_REFERER'):
        if 'login' in request.META.get('HTTP_REFERER'):
          return shortcuts.redirect('ctstem:home')
        else:
          return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))
      else:
        return shortcuts.redirect('ctstem:home')

    if request.method == 'GET':
      steps = models.Step.objects.all().filter(curriculum=curriculum)
      attachments = models.Attachment.objects.all().filter(Q(curriculum=curriculum) | Q(curriculum=curriculum.unit), teacher_only=False)
      systems = models.System.objects.all()
      total_steps = len(steps)

      # for assessment go to the first step
      if curriculum.curriculum_type != 'U' and curriculum.curriculum_type != 'L' and step_order == -1:
        step_order = 0

      context = {'curriculum': curriculum, 'attachments': attachments, 'systems': systems, 'total_steps': total_steps, 'step_order': step_order}

      if int(step_order) > 0:
        step = steps.get(order=int(step_order))
        context['step'] = step

      context['steps'] = steps

      return render(request, 'ctstem_app/CurriculumActivityPreview.html', context)

    return http.HttpResponseNotAllowed(['GET'])

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested curriculum not found</h1>')

####################################
# PREVIEW A Curriculum
####################################
def previewCurriculum(request, id=''):
  try:
    # check curriculum permission
    has_permission = check_curriculum_permission(request, id, 'preview')
    if has_permission:
      curriculum = models.Curriculum.objects.get(id=id)
    else:
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.method == 'GET':
      systems = models.System.objects.all()

      teacher_attachments = None
      student_attachments = models.Attachment.objects.all().filter(Q(curriculum=curriculum) | Q(curriculum=curriculum.unit), teacher_only=False)
      if request.user.is_authenticated or not hasattr(request.user, 'student'):
        teacher_attachments = models.Attachment.objects.all().filter(Q(curriculum=curriculum) | Q(curriculum=curriculum.unit), teacher_only=True)

      if curriculum.unit and curriculum.unit.icon:
        icon = curriculum.unit.icon.url
      elif curriculum.icon:
        icon = curriculum.icon.url
      elif curriculum.curriculum_type == 'U':
        icon = '/static/img/unit.png'
      elif curriculum.curriculum_type == 'L':
        icon = '/static/img/lesson.png'
      else:
        icon = '/static/img/assessment.png'

      context = {'curriculum': curriculum, 'systems': systems, 'icon': icon, 'student_attachments': student_attachments, 'teacher_attachments': teacher_attachments}

      return render(request, 'ctstem_app/CurriculumPreview.html', context)

    return http.HttpResponseNotAllowed(['GET'])

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested curriculum not found</h1>')

####################################
# Restore a curriculum after being deleted
####################################
def restoreCurriculum(request, id=''):
  try:
    # check if user has privilege to restore a deleted curriculum
    has_permission = check_curriculum_permission(request, id, 'restore')

    if has_permission:
      curriculum = models.Curriculum.objects.get(id=id)
      curriculum.status = 'A'
      curriculum.save()
      if curriculum.curriculum_type == 'U':
        reorder_underlying_curricula(request, curriculum.id)

      messages.success(request, "The curriculum %s has been restored and marked as Archived" % curriculum.title)

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested curriculum not found</h1>')

####################################
# Lesson PDF
####################################
def pdfCurriculum(request, id='', pdf='0'):
  try:
    # check if the lesson exists
    if '' != id:
      curriculum = models.Curriculum.objects.get(id=id)
    else:
      curriculum = models.Curriculum()

    if request.method == 'GET':
      steps = models.Step.objects.all().filter(curriculum=curriculum)
      attachments = models.Attachment.objects.all().filter(curriculum=curriculum)

      context = {'curriculum': curriculum, 'attachments': attachments, 'steps':steps}
      #print settings.STATIC_ROOT
      #return render_to_pdf_response('ctstem_app/CurriculumPDF.html', context, u'%s.%s'%(curriculum.slug, 'pdf') )
      return render_to_pdf('ctstem_app/CurriculumPDF.html', context, request)


    return http.HttpResponseNotAllowed(['GET'])

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested lesson not found</h1>')

def fetch_resources(uri, rel):
  if 'http' in uri:
    return uri
  else:
    path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    return path

def render_to_pdf(template_src, context_dict, request):
  html  = render_to_string(template_src, context_dict, request)
  result = StringIO.StringIO()
  pdf = pisa.pisaDocument(StringIO.StringIO(html.encode('utf-8')), dest=result, link_callback=fetch_resources, encoding='utf-8')
  if not pdf.err:
    return http.HttpResponse(result.getvalue(), content_type='application/pdf')
  return http.HttpResponse('We had some errors! %s' % escape(html))


####################################
# Download Lesson attachments
####################################
def downloadAttachments(request, id='', flag='S'):
  try:
    # check if the lesson exists
    if '' != id:
      curriculum = models.Curriculum.objects.get(id=id)
    else:
      raise models.Curriculum.DoesNotExist

    if request.method == 'GET' or request.method == 'POST':
      # Files (local path) to put in the .zip
      # FIXME: Change this (get paths from DB etc)
      attachments = teacher_only = None
      download_allowed = False
      if request.user.is_authenticated:
        if hasattr(request.user, 'student'):
          if flag == 'S':
            teacher_only = False
            download_allowed = True
        else:
          if flag == 'S':
            teacher_only = False
            download_allowed = True
          elif flag == 'T':
            teacher_only = True
            download_allowed = True
          else:
           download_allowed = True
      else:
        if flag == 'S':
          teacher_only = False
          download_allowed = True

      if download_allowed:
        if teacher_only is None:
          attachments = models.Attachment.objects.all().filter(Q(curriculum=curriculum) | Q(curriculum=curriculum.unit))
        else:
          attachments = models.Attachment.objects.all().filter(Q(curriculum=curriculum) | Q(curriculum=curriculum.unit), teacher_only=teacher_only)
      else:
        models.Attachment.DoesNotExist

      # Folder name in ZIP archive which contains the above files
      # E.g [thearchive.zip]/somefiles/file2.txt
      # FIXME: Set this to something better
      zip_subdir = curriculum.title
      zip_filename = "%s.zip" % zip_subdir

      # Grab ZIP file from in-memory, make response with correct MIME-type
      response = http.HttpResponse(content_type="application/x-zip-compressed")

      # The zip compressor
      zf = zipfile.ZipFile(response, "w")

      for attachment in attachments:
        # Calculate path for file in zip
        file = attachment.file_object
        fname = attachment.file_object.name.split('/')[-1]
        urlretrieve(file.url,"/tmp/%s"%fname)
        #fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write("/tmp/%s"%fname, zip_path)
        os.remove("/tmp/%s"%fname)

      # Must close zip for all contents to be written
      zf.close()

      # ..and correct content-disposition
      response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

      return response

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested Curriculum not found</h1>')




####################################
# Soft DELETE a curriculum
####################################
def deleteCurriculum(request, id=''):
  try:
    # check if the user has permission to delete a curriculum
    has_permission = check_curriculum_permission(request, id, 'delete')

    if not has_permission:
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.method == 'GET' or request.method == 'POST':
      curriculum = models.Curriculum.objects.get(id=id)
      unit = curriculum.unit
      referer = request.META.get('HTTP_REFERER')

      curriculum.status = 'R'
      curriculum.save()
      #reorder remaining underlying curricula in the unit
      if curriculum.unit:
        reorder_underlying_curricula(request, curriculum.unit.id)

      messages.success(request, "Curriculum '%s - v%s.' has been deleted" % (curriculum.title, curriculum.version))

      redirect_url = ''
      #this request came from curriculum preview page
      if 'preview' in referer:
        #if underlying curriculum, redirect to unit overview page
        if unit:
          redirect_url = '/curriculum/preview/%s' % unit.id
        #if standalone curriculum, redirect to curricula tile page
        else:
          redirect_url = '/curriculatiles/'
      #this request came from curriculum edit page
      elif 'curriculum' in referer:
        #if underlying curriculum, redirect to unit edit page
        if unit:
          redirect_url = '/curriculum/%s' % unit.id
        #if standalone curriculum, redirect to curricula tile page
        else:
          redirect_url = '/curriculatiles/'
      #this request came from curricula table page, redirect to the same page
      elif 'curricula' in referer:
        redirect_url = referer

      return http.HttpResponseRedirect(redirect_url)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assessment not found</h1>')

####################################
# Curriculum Copy
####################################
def copyCurriculum(request, id=''):
  try:

    # check if the user has permission to copy a curriculum
    has_permission = check_curriculum_permission(request, id, 'copy')

    if not has_permission:
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.method == 'GET' or request.method == 'POST':
      original_curriculum = models.Curriculum.objects.get(id=id)
      new_curriculum = copyCurriculumMeta(request, id)
      # non unit copy
      if original_curriculum.curriculum_type != 'U':
        copyCurriculumSteps(request, original_curriculum, new_curriculum)
        # if copying an underlying curricula, add the new curriculum at the end of the list
        if new_curriculum.unit:
          new_curriculum.order = None
          new_curriculum.save()
          reorder_underlying_curricula(request, new_curriculum.unit.id)
      else:
        #unit copy
        #copy underlying lessons
        if hasattr(request.user, 'teacher') or hasattr(request.user, 'researcher'):
          underlying_curriculum =  original_curriculum.underlying_curriculum.all().filter(Q(status='P') | Q(unit__collaborators=request.user)).exclude(status='R').distinct()
        else:
          underlying_curriculum = original_curriculum.underlying_curriculum.all().exclude(status='R').distinct()

        for lesson in underlying_curriculum:
          new_lesson = copyCurriculumMeta(request, lesson.id)
          copyCurriculumSteps(request, lesson, new_lesson)
          new_lesson.unit = new_curriculum
          new_lesson.save()
        reorder_underlying_curricula(request, new_curriculum.id)


      if hasattr(request.user, 'teacher'):
        messages.success(request, "A new curriculum '%s - v%s.' has been created and added to your My Curricula collection.  You may edit the newly copied curriculum after dismissing this message." % (new_curriculum.title, new_curriculum.version), extra_tags="modal_message")
      else:
        messages.success(request, "A new curriculum '%s - v%s.' has been created and the status set to Private.  You may edit the newly copied curriculum after dismissing this message." % (new_curriculum.title, new_curriculum.version), extra_tags="modal_message")

      return shortcuts.redirect('/curriculum/%s' % new_curriculum.id)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested curriculum not found</h1>')

@login_required
def copyCurriculumMeta(request, id=''):
  if '' != id:
    curriculum = models.Curriculum.objects.get(id=id)
    steps = models.Step.objects.all().filter(curriculum=curriculum)
    attachments = models.Attachment.objects.all().filter(curriculum=curriculum)
    title = curriculum.title
    collaborators = models.CurriculumCollaborator.objects.all().filter(curriculum=curriculum)
    #curriculum.title = str(datetime.datetime.now())
    curriculum.pk = None
    curriculum.id = None
    curriculum.icon = None
    curriculum.save()

    original_curriculum = models.Curriculum.objects.get(id=id)

    curriculum.created_date = datetime.datetime.now()
    curriculum.modified_date = datetime.datetime.now()
    curriculum.parent = original_curriculum
    curriculum.status = 'D'
    curriculum.version = int(original_curriculum.version) + 1
    curriculum.subject = original_curriculum.subject.all()
    curriculum.taxonomy = original_curriculum.taxonomy.all()
    curriculum.feature_rank = None

    if original_curriculum.icon:
      try:
        source = original_curriculum.icon
        filecontent = ContentFile(source.file.read())
        filename = os.path.split(source.file.name)[-1]
        filename_array = filename.split('.')
        new_filename = filename_array[0] + '-' + str(curriculum.id) + '.' + filename_array[1]
        curriculum.icon.save(new_filename, filecontent)
        curriculum.save()
        source.file.close()
        original_curriculum.icon.save(filename, filecontent)
        original_curriculum.save()
      except IOError as e:
        curriculum.save()
    else:
      curriculum.save()

    for attachment in attachments:
      if attachment.file_object:
        try:
          original_attachment_id = attachment.id
          source = attachment.file_object
          filecontent = ContentFile(source.file.read())
          filename = os.path.split(source.file.name)[-1]
          filename_array = filename.split('.')
          new_filename = filename_array[0] + '-' + str(curriculum.id) + '.' + filename_array[1]
          attachment.pk = None
          attachment.id = None
          attachment.curriculum = curriculum
          attachment.file_object.save(new_filename, filecontent)
          attachment.save()
          source.file.close()
          original_attachment = models.Attachment.objects.get(id=original_attachment_id)
          original_attachment.file_object.save(filename, filecontent)
          original_attachment.save()
        except IOError as e:
          continue

    #copy collaborators to new curriculum only for unit and stand alone lessons
    if not original_curriculum.unit:
      for collaborator in collaborators:
        collaborator.pk = None
        collaborator.id = None
        collaborator.curriculum = curriculum
        collaborator.privilege = 'V'
        collaborator.order = None
        collaborator.save()

      author, created = models.CurriculumCollaborator.objects.get_or_create(curriculum=curriculum, user=request.user)
      author.privilege = 'E'
      author.order = 1
      author.save()

    return curriculum
  else:
    return None

@login_required
def copyCurriculumSteps(request, original_curriculum, new_curriculum):
  import os
  now = datetime.datetime.now()
  dt = now.strftime("%Y-%m-%d-%H-%M-%S-%f")

  steps = models.Step.objects.all().filter(curriculum=original_curriculum)
  for step in steps:
    step_questions = models.CurriculumQuestion.objects.all().filter(step=step)
    step.pk = None
    step.id = None
    step.curriculum = new_curriculum
    step.save()
    for step_question in step_questions:
      question = step_question.question
      original_question_id = question.id
      question.id = None
      question.pk = None
      if question.sketch_background:
        try:
          source = question.sketch_background
          filecontent = ContentFile(source.file.read())
          filename = os.path.split(source.file.name)[-1]
          filename_array = filename.split('.')
          new_filename = filename_array[0][:10] + '_' + dt + '.' + filename_array[1]
          question.sketch_background.save(new_filename, filecontent)
          source.file.close()
          original_question = models.Question.objects.get(id=original_question_id)
          original_question.sketch_background.save(filename, filecontent)
          original_question.save()
        except IOError as e:
          question.sketch_background = None
      question.save()

      step_question.id = None
      step_question.pk = None
      step_question.question = question
      step_question.step = step
      step_question.save()
  return

@login_required
def archiveCurriculum(request, id=''):
  try:
    # check if the user has permission to create or modify a curriculum
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False and hasattr(request.user, 'author') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to modify this curriculum</h1>')
    # check if the curriculum exists
    else:
      if request.method == 'GET' or request.method == 'POST':
        if '' != id:
          curriculum = models.Curriculum.objects.get(id=id)
          #archive unit lessons first
          if curriculum.curriculum_type == 'U':
            for lesson in curriculum.underlying_curriculum.all():
              lesson.status = 'A'
              lesson.save()

          curriculum.status = 'A'
          curriculum.save()
        return
      return http.HttpResponseNotAllowed(['GET', 'POST'])
  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested curriculum not found</h1>')

@login_required
def bookmarkCurriculum(request, id=''):
  try:
    # check if the user has permission to bookmark a curriculum
    if hasattr(request.user, 'teacher') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to bookmark this curriculum</h1>')
    # check if the lesson exists
    if '' != id:
      curriculum = models.Curriculum.objects.get(id=id)
    else:
      raise models.Curriculum.DoesNotExist

    if request.method == 'GET' or request.method == 'POST':
      bookmark, created = models.BookmarkedCurriculum.objects.get_or_create(curriculum=curriculum, teacher=request.user.teacher)
      bookmark.save()
      return http.HttpResponse(json.dumps({}), content_type="application/json")

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested curriculum not found</h1>')

@login_required
def removeBookmark(request, id=''):
  try:
    # check if the user has permission to bookmark a curriculum
    if hasattr(request.user, 'teacher') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to remove bookmark from this curriculum</h1>')
    # check if the lesson exists
    if '' != id:
      curriculum = models.Curriculum.objects.get(id=id)
    else:
      raise models.Curriculum.DoesNotExist

    if request.method == 'GET' or request.method == 'POST':
      bookmark = models.BookmarkedCurriculum.objects.get(curriculum=curriculum, teacher=request.user.teacher)
      bookmark.delete()
      return http.HttpResponse(json.dumps({}), content_type="application/json")

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested curriculum not found</h1>')
  except models.BookmarkedCurriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested bookmark not found</h1>')



####################################
# Assign curriculum to classes
####################################
def assignCurriculum(request, id=''):
  try:
    has_permission = check_curriculum_permission(request, id, 'assign')
    if not has_permission:
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    # check if the user has permission to assign a curriculum
    if hasattr(request.user, 'administrator'):
      groups = models.UserGroup.objects.all().filter(is_active=True)
    elif hasattr(request.user, 'school_administrator'):
      groups = models.UserGroup.objects.all().filter(teacher__school = request.user.school_administrator.school, is_active=True)
    elif hasattr(request.user, 'teacher'):
      groups = models.UserGroup.objects.all().filter(Q(teacher=request.user.teacher) | Q(shared_with=request.user.teacher), Q(is_active=True)).distinct()

    curriculum = models.Curriculum.objects.get(id=id)
    #check if curriculum is stand alone or a unit
    if curriculum.curriculum_type == 'U':
      curriculum_list = underlyingCurriculum(request, 'assign', curriculum.id)
    else:
      curriculum_list = models.Curriculum.objects.all().filter(id=curriculum.id)

    assignments = models.Assignment.objects.all().filter(curriculum__in=curriculum_list, group__in=groups)
    assignment_count = {}
    instances = {}
    for group in groups:
      instances[group.id] = {}
      assignment_count[group.id] = {}
      if curriculum.curriculum_type == 'U':
        assignment_count[group.id][curriculum.id] = assignments.filter(group=group).count()
        instances[group.id][curriculum.id] = models.AssignmentInstance.objects.all().filter(assignment__curriculum__unit=curriculum, assignment__group=group).count()

      for curr in curriculum_list:
        assignment_count[group.id][curr.id] = assignments.filter(group=group, curriculum=curr).count()
        instances[group.id][curr.id] = models.AssignmentInstance.objects.all().filter(assignment__curriculum=curr, assignment__group=group).count()

    if request.method == 'GET':
      context = {'curriculum': curriculum, 'curriculum_list': curriculum_list, 'groups': groups, 'assignments': assignments, 'instances': instances, 'assignment_count': assignment_count}
      return render(request, 'ctstem_app/CurriculumAssignment.html', context)
    elif request.method == 'POST':
      data = request.POST.copy()
      #iterate over all possible (group, curriculum) assignment combinations
      for group in groups:
        for curr in curriculum_list:
          #check if an assignment already exists
          assignment = assignments.filter(group=group, curriculum=curr).first()
          assigned_key = 'assigned_%s_%s'%(str(group.id), str(curr.id))
          #if assignment already exists, but is unchecked
          if assignment:
            if assigned_key not in data:
              #assignment has been unmarked for deletion
              assignment.delete()
          else:
            #check if new assignment has been made
            if assigned_key in data and data[assigned_key]:
              #check if the new assignment is an assessment
              lock_on_completion = False
              if curr.curriculum_type == 'A':
                #lock on completion by default
                lock_on_completion = True
              new_assignment = models.Assignment(curriculum=curr, group=group, lock_on_completion=lock_on_completion)
              new_assignment.save()

      if hasattr(request.user, 'teacher'):
        response_data = {'message': 'The curriculum "%s" has been assigned.  Go to your <a href="/groups/active/">Teacher Dashboard</a> to manage your classes and assignments.' % curriculum.title}
      else:
        response_data = {'message': 'The curriculum "%s" has been assigned' % curriculum.title}
      return http.HttpResponse(json.dumps(response_data), content_type="application/json")

    return http.HttpResponseNotAllowed(['GET', 'POST'])
  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested curriculum not found</h1>')



####################################
# PRE-REGISTER
# if student email exists, add them to the class
# else redirect to the full registration page with prepopulated email
####################################
def preregister(request, group_code=''):
  if group_code:
    group = models.UserGroup.objects.get(group_code__iexact=group_code)
    group_id = group.id
    school = group.teacher.school

    if request.method == 'GET':
      form = forms.PreRegistrationForm()
      context = {'form': form, 'group_code': group_code}
      return render(request, 'ctstem_app/PreRegistration.html', context)

    elif request.method == 'POST':
      response_data = {}
      form = forms.PreRegistrationForm(data=request.POST)
      if form.is_valid(group_id):
        email = form.cleaned_data['email']
        try:
          #if student exists, add them to the class and send a notification
          student = models.Student.objects.get(user__email=email)
          membership, created = models.Membership.objects.get_or_create(student=student, group=group)
          send_added_to_group_confirmation_email(email, group)
          response_data['success'] = True
          response_data['message'] ='You have been added to the class %s.  You may now login to do your assignments. An email has been sent with instructions on resetting your password.' % group.title
          response_data['redirect_url'] = '/'

        except models.Student.DoesNotExist:
          # if student does not exist, redirect to a full registration form
          response_data['success'] = True
          response_data['redirect_url'] = "/?next=/register/group/%s/%s/" %(group_code, email)

      else:
        context = {'form': form, 'group_code': group_code}
        response_data['success'] = False
        response_data['html'] = render_to_string('ctstem_app/PreRegistration.html', context, request)

      return http.HttpResponse(json.dumps(response_data), content_type="application/json")

    return http.HttpResponseNotAllowed(['GET', 'POST'])
  else:
    return http.HttpResponseNotFound('<h1>Invalid URL</h1>')

####################################
# REGISTER
####################################
def register(request, group_code='', email=''):
  group_id = None
  if group_code:
    group = models.UserGroup.objects.get(group_code__iexact=group_code)
    group_id = group.id
    school = group.teacher.school
  else:
    if hasattr(request.user, 'school_administrator'):
      school = request.user.school_administrator.school
    elif hasattr(request.user, 'teacher'):
      school = request.user.teacher.school
    else:
      school = models.School()

    other_school = models.School.objects.get(school_code='OTHER')

  if request.method == 'POST':
    #print request.POST.copy()
    school_form = None
    new_school = None
    response_data = {}
    if group_id:
      form = forms.RegistrationForm(user=request.user, data=request.POST, group_id=group_id)
    else:
      form = forms.RegistrationForm(user=request.user, data=request.POST)
      school_form = forms.SchoolForm(data=request.POST, instance=school, prefix="school")

    if form.is_valid():
      # checking for bot signup
      # anonymous users signing up as teachers need to go through recaptcha validation
      if request.user.is_anonymous and group_id is None:
        recaptcha_response = request.POST.get('g-recaptcha-response')
        is_human = validate_recaptcha(request, recaptcha_response)
        if not is_human:
          context = {'form': form, 'school_form': school_form, 'other_school': other_school, 'recaptcha_error':  'Invalid reCAPTCHA'}
          response_data['success'] = False
          response_data['html'] = render_to_string('ctstem_app/RegistrationModal.html', context, request)
          return http.HttpResponse(json.dumps(response_data), content_type="application/json")

      #convert username to lowercase
      username = form.cleaned_data['username'].lower()
      user = User.objects.create_user(username,
                                      form.cleaned_data['email'].lower(),
                                      form.cleaned_data['password1'])
      user.first_name = form.cleaned_data['first_name']
      user.last_name = form.cleaned_data['last_name']
      #Admin, Researcher, Author, School Admin or Teacher account created by anonymous user is set as inactive
      if form.cleaned_data['account_type'] in  ['A', 'R', 'C', 'P', 'T'] and request.user.is_anonymous:
          user.is_active = False
      else:
          user.is_active = True
      user.save()

      role = ''
      if form.cleaned_data['account_type'] == 'T' or form.cleaned_data['account_type'] == 'P':
        if form.cleaned_data['account_type'] == 'T':
          newUser = models.Teacher()
          #generate validation code
          newUser.validation_code = get_random_string(length=5)
          role = 'teacher'
        else:
          newUser = models.SchoolAdministrator()
          role = 'school administrator'

        #get the school id
        selected_school = form.cleaned_data['school']
        if selected_school.school_code == 'OTHER':
          if school_form.is_valid():
            #create a new school entry
            new_school = school_form.save(commit=False)
            if user.is_active:
              new_school.is_active = True
            new_school.save()
            newUser.school = new_school
          else:
            print(school_form.errors)
            user.delete()
            context = {'form': form, 'school_form': school_form, 'other_school': other_school }
            response_data['success'] = False
            response_data['html'] = render_to_string('ctstem_app/RegistrationModal.html', context, request)
            return http.HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
          newUser.school = form.cleaned_data['school']
        newUser.user = user
        newUser.save()

      elif form.cleaned_data['account_type'] == 'S':
        newUser = models.Student()
        if group_id:
          newUser.school = school
        else:
          newUser.school = form.cleaned_data['school']
        newUser.user = user
        newUser.save()
        if group_id:
          membership, created = models.Membership.objects.get_or_create(student=newUser, group=group)

        role = 'student'

      elif form.cleaned_data['account_type'] == 'A':
        newUser = models.Administrator()
        newUser.user = user
        newUser.save()
        role = 'site admin'

      elif form.cleaned_data['account_type'] == 'R':
        newUser = models.Researcher()
        newUser.user = user
        newUser.save()
        role = 'researcher'
      elif form.cleaned_data['account_type'] == 'C':
        newUser = models.Author()
        newUser.user = user
        newUser.save()
        role = 'content author'

      current_site = Site.objects.get_current()
      domain = current_site.domain

      #anonymous user creates an account
      if request.user.is_anonymous:
        #account type created is Admin, Researcher, Content Author, School Principal
        if form.cleaned_data['account_type'] in ['A', 'R', 'C', 'P']:
          #send an email to the registering user
          send_account_pending_email(role, newUser.user)
          response_data['success'] = True
          response_data['message'] = 'Your account is pending admin approval.  You will be notified once your account is approved.'


        #account type created is Teacher
        elif form.cleaned_data['account_type'] == 'T':
          #send an email with the username and validation code to validate the account
          send_teacher_account_validation_email(newUser)
          response_data['success'] = True
          response_data['message'] = 'An email has been sent to %s to validate your account.  Please validate your account with in 24 hours.' % newUser.user.email


        #account type created is Student
        elif form.cleaned_data['account_type'] == 'S':
          new_user = authenticate(username=form.cleaned_data['username'].lower(),
                                  password=form.cleaned_data['password1'],)
          login(request, new_user)
          messages.info(request, 'Your have successfully registered.')

          send_student_account_by_self_confirmation_email(newUser.user, group)
          response_data['success'] = True

        else:
          response_data['success'] = False
          messages.error(request, 'Sorry you cannot create this user account')

        response_data['redirect_url'] = '/'

      else:
        response_data['message'] = '%s account has been created.' % role.title()
        send_account_by_admin_confirmation_email(role, newUser.user, form.cleaned_data['password1'])
        url = '/'
        if form.cleaned_data['account_type'] == 'A':
          url = '/users/admins'
        elif form.cleaned_data['account_type'] == 'R':
          url = '/users/researchers'
        elif form.cleaned_data['account_type'] == 'P':
          url = '/users/school_administrators'
        elif form.cleaned_data['account_type'] == 'C':
          url = '/users/authors'
        elif form.cleaned_data['account_type'] == 'T':
          url = '/users/teachers'
        elif form.cleaned_data['account_type'] == 'S':
          url = '/users/students'

        response_data['success'] = True
        response_data['redirect_url'] = url

    else:
      print(form.errors)
      if group_id:
        context = {'form': form, 'group_id': group_id, 'school_id': school.id, 'group_code': group_code, 'email': email}
      else:
        school_form.is_valid()
        context = {'form': form, 'school_form': school_form, 'other_school': other_school }
      response_data['success'] = False
      response_data['html'] = render_to_string('ctstem_app/RegistrationModal.html', context, request)

    return http.HttpResponse(json.dumps(response_data), content_type="application/json")

  ########### GET ###################
  else:
    print(request.user)

    if hasattr(request.user, 'researcher') or hasattr(request.user, 'author') or hasattr(request.user, 'student'):
      messages.error(request, 'You do not have the privilege to register any other user')
      return shortcuts.redirect('ctstem:home')

    if group_id:
      if email:
        form = forms.RegistrationForm(initial={'email': email}, user=request.user, group_id=group_id)
        context = {'form': form, 'group_id': group_id, 'school_id': school.id, 'group_code': group_code, 'email': email}
      else:
        form = forms.RegistrationForm(user=request.user, group_id=group_id)
        context = {'form': form, 'group_id': group_id, 'school_id': school.id, 'group_code': group_code}
    elif request.user.is_anonymous:
      form = forms.RegistrationForm(user=request.user)
      school_form = forms.SchoolForm(instance=school, prefix='school')
      context = {'form': form, 'school_form': school_form, 'other_school': other_school}
    elif hasattr(request.user, 'school_administrator'):
      school = request.user.school_administrator.school
      print(school.id)
      form = forms.RegistrationForm(user=request.user)
      context = {'form': form, 'school_id': school.id}
    elif hasattr(request.user, 'teacher'):
      school = request.user.teacher.school
      form = forms.RegistrationForm(user=request.user)
      context = {'form': form, 'school_id': school.id}
    else:
      form = forms.RegistrationForm(user=request.user)
      school_form = forms.SchoolForm(instance=school, prefix='school')
      context = {'form': form, 'school_form': school_form, 'other_school': other_school}

    return render(request, 'ctstem_app/RegistrationModal.html', context)

####################################
# Validate reCAPTCHA response during
# registration
####################################
def validate_recaptcha(request, recaptcha_response):
  url = 'https://www.google.com/recaptcha/api/siteverify'
  values = {
    'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
    'response': recaptcha_response
  }
  data = urllib.parse.urlencode(values).encode("utf-8")
  req = urllib.request.Request(url, data)
  response = urllib.request.urlopen(req)
  result = json.load(response)

  if result['success']:
    return True
  else:
    return False

####################################
# USER LOGIN
####################################
def user_login(request, user_name=''):
  username = password = ''
  print(request.method)
  redirect_url = request.GET.get('next', '')
  if request.method == 'POST':
    data = request.POST.copy()
    form = forms.LoginForm(data)
    response_data = {}
    if form.is_valid():
      username_email = form.cleaned_data['username_email'].lower()
      password = form.cleaned_data['password']
      username = None
      if User.objects.filter(username__iexact=username_email).count() == 1:
        username = username_email
      elif User.objects.filter(email__iexact=username_email).count() == 1:
        username = User.objects.get(email__iexact=username_email).username.lower()
      user = authenticate(username=username, password=password)

      if user.is_active:
        login(request, user)
        if redirect_url:
          messages.success(request, "Now you are logged in")
          response_data['success'] = True
          response_data['redirect_url'] = redirect_url

        elif hasattr(user, 'teacher'):
          messages.success(request, "Welcome to the CT-STEM website. If you need help with using the site, you can go to the <a href='/help'>Help and FAQ</a> page.", extra_tags='safe');
          response_data['success'] = True
          response_data['redirect_url'] = '/groups/active/'

        else:
          messages.success(request, "You have logged in")
          response_data['success'] = True
          response_data['redirect_url'] = '/'

      else:
        messages.error(request, 'Your account has not been activated')
        context = {'form': form, 'redirect_url': redirect_url}
        response_data['success'] = False
        response_data['html'] = render_to_string('ctstem_app/LoginModal.html', context, request)
    else:
      context = {'form': form, 'redirect_url': redirect_url}
      response_data['success'] = False
      response_data['html'] = render_to_string('ctstem_app/LoginModal.html', context, request)

    return http.HttpResponse(json.dumps(response_data), content_type="application/json")
  elif request.method == 'GET':
    if user_name:
      form = forms.LoginForm(initial={'username_email': user_name})
    else:
      form = forms.LoginForm()
    context = {'form': form, 'redirect_url': redirect_url}
    return render(request, 'ctstem_app/LoginModal.html', context)

  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# USER LOGOUT
####################################
@login_required
def user_logout(request):
  logout(request)
  messages.success(request, "You have logged out")
  return shortcuts.redirect('ctstem:home')

####################################
# USER PROFILE
####################################
@login_required
def userProfile(request, id=''):
  try:
    if '' == id:
      return shortcuts.redirect('ctstem:register')
    user = User.objects.get(id=id)
    # check user role
    role = None

    if hasattr(user, 'administrator'):
      role = 'administrator'
      admin = models.Administrator.objects.get(user__id=id)
    elif hasattr(user, 'teacher'):
      role = 'teacher'
      teacher = models.Teacher.objects.get(user__id=id)
      school = teacher.school
    elif hasattr(user, 'student'):
      role = 'student'
      student = models.Student.objects.get(user__id=id)
      school = student.school
    elif hasattr(user, 'researcher'):
      role = 'researcher'
      researcher = models.Researcher.objects.get(user__id=id)
    elif hasattr(user, 'author'):
      role = 'author'
      author = models.Author.objects.get(user__id=id)
    elif hasattr(user, 'school_administrator'):
      role = 'school_administrator'
      school_administrator = models.SchoolAdministrator.objects.get(user__id=id)
      school = school_administrator.school
    else:
      return http.HttpResponseForbidden('<h1>User has no role</h1>')

    privilege = 0
    if hasattr(request.user, 'administrator'):
      privilege = 1
    elif hasattr(request.user, 'researcher') and role == 'researcher' and request.user.id == researcher.user.id:
      privilege = 1
    elif hasattr(request.user, 'school_administrator'):
      if role == 'school_administrator' and request.user.id == school_administrator.user.id:
        privilege = 1
      elif role == 'teacher' and request.user.school_administrator.school == teacher.school:
        privilege = 1
      elif role == 'student' and request.user.school_administrator.school == student.school:
        privilege = 1
    elif hasattr(request.user, 'teacher'):
      if role == 'teacher' and request.user.id == teacher.user.id:
        privilege = 1
      elif role == 'student' and request.user.teacher.school == student.school:
        privilege = 1
    elif hasattr(request.user, 'student') and role == 'student' and request.user.id == student.user.id:
      privilege = 1
    elif hasattr(request.user, 'author') and role == 'author' and request.user.id == author.user.id:
      privilege = 1

    if privilege == 0:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to view/edit this profile</h1>')

    if request.method == 'GET':
      userform = forms.UserProfileForm(instance=user, prefix='user')
      if role == 'student':
        profileform = forms.StudentForm(user=request.user, instance=student, prefix='student')
      elif role == 'teacher':
        profileform = forms.TeacherForm(user=request.user, instance=teacher, prefix='teacher')
      elif role == 'administrator':
        profileform = None
      elif role == 'researcher':
        profileform = forms.ResearcherForm(instance=researcher, prefix='researcher')
      elif role == 'author':
        profileform = forms.AuthorForm(instance=author, prefix='author')
      elif role == 'school_administrator':
        profileform = forms.SchoolAdministratorForm(user=request.user, instance=school_administrator, prefix='school_administrator')
      else:
        return http.HttpResponseNotFound('<h1>Requested user does not have a role</h1>')

      context = {'profileform': profileform, 'userform': userform, 'role': role.replace('_', ' ')}
      return render(request, 'ctstem_app/UserProfile.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      if role == 'student':
          data.__setitem__('student-user', student.user.id)
      elif role == 'teacher':
          data.__setitem__('teacher-user', teacher.user.id)
      elif role == 'administrator':
          data.__setitem__('admin-user', admin.user.id)
      elif role == 'researcher':
          data.__setitem__('researcher-user', researcher.user.id)
      elif role == 'author':
          data.__setitem__('author-user', author.user.id)
      elif role == 'school_administrator':
          data.__setitem__('school_administrator-user', school_administrator.user.id)
      #convert username and email to lowercase before save
      data.__setitem__('user-username', data.__getitem__('user-username').lower())
      data.__setitem__('user-email', data.__getitem__('user-email').lower())
      data.__setitem__('user-password', user.password)
      data.__setitem__('user-last_login', user.last_login)
      data.__setitem__('user-date_joined', user.date_joined)
      userform = forms.UserProfileForm(data, instance=user, prefix='user')

      profileform = None
      if role == 'student':
        profileform = forms.StudentForm(user=request.user, data=data, instance=student, prefix='student')
      elif role == 'teacher':
        profileform = forms.TeacherForm(user=request.user, data=data, instance=teacher, prefix='teacher')
      elif role == 'researcher':
        profileform = forms.ResearcherForm(data, instance=researcher, prefix='researcher')
      elif role == 'author':
        profileform = forms.AuthorForm(data, instance=author, prefix='author')
      elif role == 'school_administrator':
        profileform = forms.SchoolAdministratorForm(user=request.user, data=data, instance=school_administrator, prefix='school_administrator')

      if userform.is_valid(id):
        if profileform is None:
          userform.save()
          messages.success(request, "User profile saved successfully")
          context = {'userform': userform, 'role': role.replace('_', ' ')}
        elif profileform.is_valid():
          userform.save()
          profile = profileform.save()
          if role == 'teacher':
            new_school = profile.school
            # if school has changes update teacher's school
            # as well as the associated students' school
            if new_school != school:
              update_school(request, profile, new_school)
          messages.success(request, "User profile saved successfully")
          context = {'profileform': profileform, 'userform': userform, 'role': role.replace('_', ' ')}
        else:
          print(profileform.errors)
          messages.error(request, "User profile could not be saved. Please check the errors below.")
          context = {'profileform': profileform, 'userform': userform, 'role': role.replace('_', ' ')}
      else:
        print(userform.errors)
        if profileform:
          print(profileform.errors)
        messages.error(request, "User profile could not be saved. Please check the errors below.")
        context = {'profileform': profileform, 'userform': userform, 'role': role.replace('_', ' ')}

      return render(request, 'ctstem_app/UserProfile.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except User.DoesNotExist:
      return http.HttpResponseNotFound('<h1>Requested user not found</h1>')

#####################################################
# Check if the consent popup needs to be loaded
#####################################################
def load_consent(request):
  load = False
  if hasattr(request.user, 'student'):
    if request.user.student.consent == 'U':
      load = True
  elif hasattr(request.user, 'teacher'):
    if request.user.teacher.consent == 'U':
      teacher = models.Teacher.objects.get(user=request.user)
      teacher.consent = 'A'
      teacher.save()
      load = True

  response_data = {}
  response_data['load'] = load
  return http.HttpResponse(json.dumps(response_data), content_type="application/json")

####################################
# Student/Teacher consent
####################################
def consent(request):
  if hasattr(request.user, 'student') == False and hasattr(request.user, 'teacher') == False:
    http.HttpResponseNotFound('<h1>You do not have the privilege to access this form</h1>')

  if request.method == 'GET':
    if hasattr(request.user, 'student'):
      student = request.user.student
      form = forms.ConsentForm(instance=student, prefix='student')
      context = {'form': form}
    else:
      context = {}
    return render(request, 'ctstem_app/ConsentModal.html', context)
  elif request.method == 'POST':
    data = request.POST.copy()
    student = request.user.student
    form = forms.ConsentForm(data, instance=student, prefix='student')
    response_data = {}
    if form.is_valid():
      form.save()
      response_data['success'] = True
      messages.success(request, "Thank you for submitting the opt-in form")
    else:
      response_data['success'] = False
      response_data['message'] = 'Please select "I Agree" or "I Disagree" and submit this form to proceed'
    return http.HttpResponse(json.dumps(response_data), content_type="application/json")


####################################
# DELETE USER
####################################
def deleteUser(request, id=''):
  try:
    # check if the lesson exists
    if '' != id:
      user = User.objects.get(id=id)

    privilege = 1
    # check if the user has permission to delete a user
    if request.user.is_anonymous:
      privilege = 0
    elif hasattr(request.user, 'author') or hasattr(request.user, 'student') or hasattr(request.user, 'researcher'):
      privilege = 0
    elif hasattr(request.user, 'school_administrator'):
      if hasattr(user, 'administrator') or hasattr(user, 'researcher') or hasattr(user, 'author'):
        privilege = 0
      elif hasattr(user, 'teacher') and user.teacher.school != request.user.school_administrator.school:
        privilege = 0
      elif hasattr(user, 'student') and user.student.school != request.user.school_administrator.school:
        privilege = 0
    elif hasattr(request.user, 'teacher'):
      if hasattr(user, 'administrator') or hasattr(user, 'researcher') or hasattr(user, 'author') or hasattr(user, 'teacher') or hasattr(user, 'school_administrator'):
        privilege = 0
      elif hasattr(user, 'student') and user.student.school != request.user.teacher.school:
        privilege = 0

    if privilege == 0:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to delete this user</h1>')

    if request.method == 'GET' or request.method == 'POST':
      # check if the user has authored any curriculum and transfer the ownership to an admin
      flag = transferCurriculum(request, user)
      if flag:
        user.delete()
        messages.success(request, '%s deleted' % user.username)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except User.DoesNotExist:
    return http.HttpResponseNotFound('<h1>User not found</h1>')

####################################
# When deleting a user, transfer the curriculum
# authored by this user to an admin
####################################
def transferCurriculum(request, user):
  curricula = models.Curriculum.objects.all().filter(curriculumcollaborator__user=user, curriculumcollaborator__privilege='E')
  flag = True
  if len(curricula) > 0:
    #get an admin to transfer the curriculum ownership to
    admin = models.Administrator.objects.all().order_by('user__date_joined')[0]
    if admin:
      for curriculum in curricula:
        # if the curriculum has only one author, set the author to an admin
        if models.CurriculumCollaborator.objects.all().filter(curriculum=curriculum, privilege='E').count() == 1:
          models.CurriculumCollaborator.objects.create(curriculum=curriculum, user=admin.user, order=1, privilege='E')
      messages.success(request, 'Curriculum owned by %s has been trasferred to %s' % (user.username, admin.user.username))
    else:
      messages.success(request, 'No admins exists to transfer ownership of curriculum authored by %s. So the user cannot be deleted.' % user.username)
      flag = False
  return flag

####################################
# Remove student from the group
# but do not delete the student account from the system
####################################
def removeStudent(request, group_id='', student_id=''):
  try:
    # check if the user has permission to create or modify a group
    has_permission = check_group_permission(request, group_id)
    if not has_permission:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to remove users from this class</h1>')

    group = models.UserGroup.objects.get(id=group_id)
    student = models.Student.objects.get(id=student_id)

    if request.method == 'GET' or request.method == 'POST':
      membership = models.Membership.objects.get(group=group, student=student)
      membership.delete()
      response_data = {'result': 'Success'}
      return http.HttpResponse(json.dumps(response_data), content_type="application/json")

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.UserGroup.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested class not found</h1>')
  except models.Student.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested student not found</h1>')

####################################
# Add an existing student to the group
# and send an email notification to the student
####################################
def addStudent(request, group_id='', student_id=''):
  try:
    # check if the user has permission to create or modify a group
    has_permission = check_group_permission(request, group_id)
    if not has_permission:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to add students to this class</h1>')

    group = models.UserGroup.objects.get(id=group_id)
    student = models.Student.objects.get(id=student_id)

    if request.method == 'POST':
      membership = models.Membership.objects.get_or_create(group=group, student=student)
      send_added_to_group_confirmation_email(student.user.email, group)
      response_data = {'result': 'Success'}
      return http.HttpResponse(json.dumps(response_data), content_type="application/json")

    return http.HttpResponseNotAllowed(['POST'])

  except models.UserGroup.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested class not found</h1>')
  except models.Student.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested student not found</h1>')

####################################
# Create a new student account and add them to the group
# Then send an email notification to the student
####################################
def createStudent(request, group_id=''):
  try:
    # check if the user has permission to create a student
    import re
    # check if the user has permission to create or modify a group
    has_permission = check_group_permission(request, group_id)
    if not has_permission:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to add students from this class</h1>')

    if request.method == 'POST':
      data=request.POST
      response_data = {}
      username = data['username'].lower()
      email = data['email']
      first_name = data['first_name']
      last_name = data['last_name']

      if User.objects.filter(username=username).exists():
        response_data['error'] = 'The username is already in use. Please choose another.'
      elif User.objects.filter(email=email).exists():
        response_data['error'] = 'The email is already in use. Please choose another.'
      elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        response_data['error'] = 'The email format in invalid'
      else:
        #generate a random password
        password = User.objects.make_random_password()
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        #create student account
        group = models.UserGroup.objects.get(id=group_id)
        student = models.Student.objects.create(user=user, school=group.teacher.school)
        membership, created = models.Membership.objects.get_or_create(student=student, group=group)

        response_data = {'result': 'Success', 'student': {'user_id': user.id, 'student_id': student.id, 'username': user.username,
                          'name': user.get_full_name(), 'email': user.email, 'status': 'Active' if user.is_active else 'Inactive',
                          'last_login': user.last_login.strftime('%B %d, %Y') if user.last_login else '', 'group': group.id,
                          'student_consent': student.get_consent(), 'member_since': user.date_joined.strftime('%B %d, %Y')}
                        }

        send_account_by_admin_confirmation_email('student', user, password)

      return http.HttpResponse(json.dumps(response_data), content_type="application/json")
    return http.HttpResponseNotAllowed(['POST'])

  except models.UserGroup.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested class not found</h1>')
  except models.Student.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested student not found</h1>')

def notimplemented(request):
  return render(request, 'ctstem_app/NotImplemented.html')

####################################
# List of subcategories for a category
####################################
def subcategories(request, category_id=''):
  category = models.Category.objects.get(id=category_id)
  subcategories  = models.Subcategory.objects.all().filter(category__id=category_id).order_by('title')
  context = {'category': category, 'subcategories': subcategories}
  return render(request, 'ctstem_app/PracticeModal.html', context)


####################################
# List of categories for a standard
####################################
def categories(request, standard_id=''):
  categories  = models.Category.objects.all().filter(standard__id=standard_id).order_by('name')
  category_list = []
  for category in categories:
    category_list.append({'id': category.id, 'category': category.name})
  response_data = {'category_list': category_list}
  return http.HttpResponse(json.dumps(response_data), content_type="application/json")

####################################
# Table view of standards
####################################
def standards(request):
  if hasattr(request.user, 'author') == False and hasattr(request.user, 'researcher') == False and  hasattr(request.user, 'administrator') == False:
    standard = models.Standard.objects.all().filter(primary=True).order_by('name')[0]
    context = {'standard': standard}
    return render(request, 'ctstem_app/Standards.html', context)
  else:
    standards = models.Standard.objects.all().order_by('name')
    context = {'standards': standards}
    return render(request, 'ctstem_app/Standards.html', context)

####################################
# Add/Edit Standard
####################################
@login_required
def standard(request, id=''):
  try:
    if hasattr(request.user, 'author') == False and hasattr(request.user, 'researcher') == False and  hasattr(request.user, 'administrator') == False:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to add/modify standard</h1>')
    if '' != id:
      standard = models.Standard.objects.get(id=id)
    else:
      standard = models.Standard()

    if request.method == 'GET':
      form = forms.StandardForm(instance=standard, prefix='standard')
      CategoryFormSet = nestedformset_factory(models.Standard, models.Category, form=forms.CategoryForm,
                                                    nested_formset=inlineformset_factory(models.Category, models.Subcategory, form=forms.SubcategoryForm, can_delete=True, can_order=True, extra=1),
                                                    can_delete=True, can_order=True, extra=1)
      formset = CategoryFormSet(instance=standard, prefix='form')
      context = {'form': form, 'formset':formset}
      return render(request, 'ctstem_app/Standard.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      form = forms.StandardForm(data, instance=standard, prefix='standard')
      CategoryFormSet = nestedformset_factory(models.Standard, models.Category, form=forms.CategoryForm,
                                                    nested_formset=inlineformset_factory(models.Category, models.Subcategory, form=forms.SubcategoryForm, can_delete=True, can_order=True, extra=1),
                                                    can_delete=True, can_order=True, extra=1)
      formset = CategoryFormSet(data, request.FILES, instance=standard, prefix='form')
      print(form.is_valid())
      print(formset.is_valid())
      if form.is_valid() and formset.is_valid():
        savedStandard = form.save()
        formset.save(commit=False)
        for catform in formset.ordered_forms:
          catform.instance.order = catform.cleaned_data['ORDER']
          catform.instance.standard = savedStandard
          catform.instance.save()
          for subform in catform.nested.ordered_forms:
            subform.instance.category = catform.instance
            subform.instance.save()
          for obj in catform.nested.deleted_objects:
            obj.delete()
        #remove deleted questions
        for obj in formset.deleted_objects:
          obj.delete()


        messages.success(request, "Standard Saved.")
        return shortcuts.redirect('ctstem:standard', id=savedStandard.id)
      else:
        print(form.errors)
        print(formset.errors)
        messages.error(request, "The standard could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form, 'formset':formset}
        return render(request, 'ctstem_app/Standard.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Standard.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested standard not found</h1>')

####################################
# DELETE Standard
####################################
@login_required
def deleteStandard(request, id=''):
  try:
    # check if the user has permission to delete a subcategory
    if hasattr(request.user, 'author') == False and hasattr(request.user, 'researcher') == False and  hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to delete this Standard</h1>')

    standard = models.Standard.objects.get(id=id)

    if request.method == 'GET' or request.method == 'POST':
      standard.delete()
      messages.success(request, '%s deleted' % standard.name)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Standard.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Standard not found</h1>')

####################################
# Search Taxonomy
####################################
@login_required
def searchTaxonomy(request):
  # check if the user has permission to add a question
  if hasattr(request.user, 'teacher') == False and hasattr(request.user, 'author') == False and hasattr(request.user, 'researcher') == False and  hasattr(request.user, 'administrator') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege search taxonomy</h1>')

  title = 'Search Standards'
  if 'GET' == request.method:
    form = forms.TaxonomySearchForm()
    context = {'form': form, 'title': title}
    return render(request, 'ctstem_app/TaxonomySearch.html', context)

  elif 'POST' == request.method:
    data = request.POST.copy()
    query_filter = {}
    if data['standard']:
      query_filter['category__standard__id'] = int(data['standard'])
    if data['category']:
      query_filter['category__id'] = int(data['category'])
    if data['title']:
      query_filter['title__icontains'] = str(data['title'])
    if data['code']:
      query_filter['code__icontains'] = str(data['code'])
    print(query_filter)
    taxonomyList = models.Subcategory.objects.filter(**query_filter).annotate(code_isnull=models.IsNull('code')).order_by('code_isnull', Lower('code'), Lower('category__standard__short_name'), Lower('category__name'), Lower('title'))
    taxonomy_list = [{'standard': subcategory.category.standard.short_name, 'category': subcategory.category.name, 'title': subcategory.title, 'code': subcategory.code, 'id': subcategory.id} for subcategory in taxonomyList]
    return http.HttpResponse(json.dumps(taxonomy_list), content_type="application/json")

  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# Search Students
####################################
@login_required
def searchStudents(request):
  # check if the user has permission to add a question
  if hasattr(request.user, 'teacher') == False and hasattr(request.user, 'school_administrator') == False and  hasattr(request.user, 'administrator') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege search students</h1>')

  if 'GET' == request.method:
    studentSearchForm = forms.UserSearchForm()
    context = {'studentSearchForm': studentSearchForm}
    return render(request, 'ctstem_app/StudentSearch.html', context)

  elif 'POST' == request.method:
    data = request.POST.copy()
    print(data)
    query_filter = {}
    if data['username']:
      query_filter['user__username__icontains'] = str(data['username'])
    if data['first_name']:
      query_filter['user__first_name__icontains'] = str(data['first_name'])
    if data['last_name']:
      query_filter['user__last_name__icontains'] = str(data['last_name'])
    if data['email']:
      query_filter['user__email__icontains'] = str(data['email'])

    group = models.UserGroup.objects.get(id=int(data['group_id']))
    school = group.teacher.school
    query_filter['school__id'] = school.id

    studentList = models.Student.objects.filter(**query_filter)
    student_list = [{'user_id': student.user.id, 'student_id': student.id, 'username': student.user.username, 'name': student.user.get_full_name(),
                     'email': student.user.email, 'status': 'Active' if student.user.is_active else 'Inactive',
                     'last_login': student.user.last_login.strftime('%B %d, %Y') if student.user.last_login else '',
                     'group': group.id, 'student_consent': student.get_consent(),
                     'member_since': student.user.date_joined.strftime('%B %d, %Y')}
                for student in studentList]
    return http.HttpResponse(json.dumps(student_list), content_type="application/json")

  return http.HttpResponseNotAllowed(['GET', 'POST'])


####################################
# Search Teachers
####################################
@login_required
def searchTeachers(request):
  # check if the user has permission to add a question
  if request.user.is_anonymous or hasattr(request.user, 'student'):
    return http.HttpResponseNotFound('<h1>You do not have the privilege search teachers</h1>')

  if 'GET' == request.method:
    teacherSearchForm = forms.UserSearchForm()
    context = {'teacherSearchForm': teacherSearchForm}
    return render(request, 'ctstem_app/TeacherSearch.html', context)

  elif 'POST' == request.method:
    data = request.POST.copy()
    query_filter = {}
    if data['username']:
      query_filter['user__username__icontains'] = str(data['username'])
    if data['first_name']:
      query_filter['user__first_name__icontains'] = str(data['first_name'])
    if data['last_name']:
      query_filter['user__last_name__icontains'] = str(data['last_name'])
    if data['email']:
      query_filter['user__email__icontains'] = str(data['email'])

    teacherList = models.Teacher.objects.filter(**query_filter)
    teacher_list = [{'user_id': teacher.user.id, 'teacher_id': teacher.id, 'username': teacher.user.username, 'name': teacher.user.get_full_name(),
                     'email': teacher.user.email}
                for teacher in teacherList]
    return http.HttpResponse(json.dumps(teacher_list), content_type="application/json")

  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# Search Curriculum Collaborators
####################################
@login_required
def searchCollaborators(request):
  # check if the user has permission search Collaborators
  if request.user.is_anonymous or hasattr(request.user, 'student') == True:
    return http.HttpResponseNotFound('<h1>You do not have the privilege search collaborators</h1>')

  if 'GET' == request.method:
    collaboratorSearchForm = forms.UserSearchForm()
    context = {'collaboratorSearchForm': collaboratorSearchForm}
    return render(request, 'ctstem_app/CurriculumCollaboratorSearch.html', context)

  elif 'POST' == request.method:
    data = request.POST.copy()
    print(data)
    query_filter = {}
    if data['username']:
      query_filter['username__icontains'] = str(data['username'])
    if data['first_name']:
      query_filter['first_name__icontains'] = str(data['first_name'])
    if data['last_name']:
      query_filter['last_name__icontains'] = str(data['last_name'])
    if data['email']:
      query_filter['email__icontains'] = str(data['email'])

    if hasattr(request.user, 'teacher') or hasattr(request.user, 'school_administrator') or hasattr(request.user, 'researcher'):
      collaboratorList = User.objects.filter(Q(teacher__isnull=False) | Q(researcher__isnull=False)).exclude(id=request.user.id)
    else:
      collaboratorList = User.objects.filter(Q(administrator__isnull=False) | Q(researcher__isnull=False) | Q(author__isnull=False) |  Q(teacher__isnull=False))

    collaboratorList = collaboratorList.filter(**query_filter).order_by('first_name', 'last_name')
    collaborator_list = [{'user_id': user.id, 'username': user.username, 'name': user.get_full_name(),
                     'email': user.email}
                for user in collaboratorList]
    return http.HttpResponse(json.dumps(collaborator_list), content_type="application/json")

  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# Get Curriculum Collaborators
####################################
@login_required
def getCollaborators(request, id=''):
  # check if the user has permission search Collaborators
  if request.user.is_anonymous or hasattr(request.user, 'student') == True:
    return http.HttpResponseNotFound('<h1>You do not have the privilege search collaborators</h1>')

  if 'GET' == request.method:
    collaborators = models.CurriculumCollaborator.objects.all().filter(curriculum__id=id).order_by('privilege', 'order')
    collaborator_list = [{'user_id': collaborator.user.id, 'username': collaborator.user.username, 'name': collaborator.user.get_full_name(),
                     'email': collaborator.user.email, 'order': collaborator.order, 'privilege_code': collaborator.privilege, 'privilege_display': collaborator.get_privilege_display()}
                for collaborator in collaborators]

    return http.HttpResponse(json.dumps(collaborator_list), content_type="application/json")

  return http.HttpResponseNotAllowed(['GET'])

####################################
# USER LIST
####################################
@login_required
def users(request, role):

  if request.method == 'GET' or request.method == 'POST':

    search_criteria = None

    if request.method == 'POST':
      data = request.POST.copy()
      # bulk update
      id_list = []
      for key in data:
        if 'user_' in key:
          id_list.append(data[key])
      if len(id_list):
        _do_action(request, id_list, 'user')

      #search
      if 'search_criteria' in data:
        search_criteria = data['search_criteria']
      searchForm = forms.SearchForm(data)
    else:
      searchForm = forms.SearchForm()

    privilege = 0
    if hasattr(request.user, 'administrator'):
      privilege = 5
    elif hasattr(request.user, 'researcher'):
      privilege = 4
    elif hasattr(request.user, 'school_administrator'):
      privilege = 3
      school = request.user.school_administrator.school
    elif hasattr(request.user, 'teacher'):
      privilege = 2
      school = request.user.teacher.school
    elif hasattr(request.user, 'student') or hasattr(request.user, 'author'):
      privilege = 1

    if role == 'students':
      if privilege > 3:
        users = models.Student.objects.all()
      elif privilege > 1:
        users = models.Student.objects.all().filter(school=school)
    elif role == 'teachers':
      if privilege > 3:
        users = models.Teacher.objects.all()
      elif privilege > 1:
        users = models.Teacher.objects.all().filter(school=school)
    elif role == 'admins' and privilege > 4:
      users = models.Administrator.objects.all()
    elif role == 'researchers' and privilege > 4:
      users = models.Researcher.objects.all()
    elif role == 'authors' and privilege > 4:
      users = models.Author.objects.all()
    elif role == 'school_administrators' and privilege > 3:
      users = models.SchoolAdministrator.objects.all()
    else:
      return http.HttpResponseNotFound('<h1>You do not have the privilege view %s</h1>'% role)

    if search_criteria:
      users = searchUsers(request, users, role, search_criteria)

    order_by = request.GET.get('order_by') or 'user__username'
    direction = request.GET.get('direction') or 'asc'
    ignorecase = request.GET.get('ignorecase') or 'false'
    sort_order = [{'order_by': order_by, 'direction': direction, 'ignorecase': ignorecase}]
    user_list = paginate(request, users, sort_order, 100)

    uploadForm = forms.UploadFileForm(user=request.user)
    assignmentForm = forms.AssignmentSearchForm(user=request.user)

    context = {'users': user_list, 'role': role, 'uploadForm': uploadForm, 'assignmentForm': assignmentForm, 'searchForm': searchForm, 'order_by': order_by, 'direction': direction}

    return render(request, 'ctstem_app/Users.html', context)

  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
#paginate the queryset based on the items per page and sort order
####################################
def paginate(request, queryset, sort_order, count=10):

  ordering_list = []

  if sort_order:
    for order in sort_order:
      order_by = order['order_by']
      direction = order['direction']
      ignorecase = order['ignorecase']

      ordering = order_by

      if ignorecase == 'true':
        ordering = Lower(ordering)
        if direction == 'desc':
          ordering = ordering.desc()
      else:
        if direction == 'desc':
          ordering = '-{}'.format(ordering)

      ordering_list.append(ordering)

    queryset = queryset.order_by(*ordering_list)

  paginator = Paginator(queryset, count)
  page = request.GET.get('page')
  try:
    object_list = paginator.page(page)
  except PageNotAnInteger:
    # If page is not an integer, deliver first page.
    object_list = paginator.page(1)
  except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
    object_list = paginator.page(paginator.num_pages)

  return object_list

####################################
# filter user queryset based on role and search criteria
####################################
def searchUsers(request, queryset, role, search_criteria):
  query_filter = Q(user__username__icontains=search_criteria)
  query_filter.add(Q(user__first_name__icontains=search_criteria), Q.OR)
  query_filter.add(Q(user__last_name__icontains=search_criteria), Q.OR)
  query_filter.add(Q(user__email__icontains=search_criteria), Q.OR)
  if role == 'students':
    query_filter.add(Q(school__name__icontains=search_criteria), Q.OR)
    query_filter.add(Q(student_membership__group__title__icontains=search_criteria), Q.OR)
  elif role == 'teachers':
    query_filter.add(Q(school__name__icontains=search_criteria), Q.OR)
    query_filter.add(Q(groups__title__icontains=search_criteria), Q.OR)
  elif role == 'school_administrators':
    query_filter.add(Q(school__name__icontains=search_criteria), Q.OR)

  result = queryset.filter(query_filter).distinct()
  return result


####################################
# filter group queryset based on search criteria
####################################
def searchGroups(request, queryset, search_criteria):
  query_filter = Q(title__icontains=search_criteria)
  query_filter.add(Q(subject__name__icontains=search_criteria), Q.OR)
  query_filter.add(Q(time__icontains=search_criteria), Q.OR)
  query_filter.add(Q(teacher__user__first_name__icontains=search_criteria), Q.OR)
  query_filter.add(Q(teacher__user__last_name__icontains=search_criteria), Q.OR)
  query_filter.add(Q(shared_with__user__first_name__icontains=search_criteria), Q.OR)
  query_filter.add(Q(shared_with__user__last_name__icontains=search_criteria), Q.OR)
  query_filter.add(Q(teacher__school__name__icontains=search_criteria), Q.OR)
  result = queryset.filter(query_filter).distinct()
  return result

####################################
# filter curricula queryset based on search criteria
####################################
def searchCurricula(request, queryset, search_criteria):
  query_filter = Q(title__icontains=search_criteria)
  query_filter.add(Q(subject__name__icontains=search_criteria), Q.OR)
  query_filter.add(Q(time__icontains=search_criteria), Q.OR)
  query_filter.add(Q(curriculumcollaborator__user__first_name__icontains=search_criteria), Q.OR)
  query_filter.add(Q(curriculumcollaborator__user__last_name__icontains=search_criteria), Q.OR)
  query_filter.add(Q(taxonomy__title__icontains=search_criteria), Q.OR)
  query_filter.add(Q(taxonomy__category__name__icontains=search_criteria), Q.OR)
  query_filter.add(Q(taxonomy__category__standard__name__icontains=search_criteria), Q.OR)
  query_filter.add(Q(status__icontains=search_criteria), Q.OR)
  result = queryset.filter(query_filter).distinct()
  return result

####################################
# filter curricula queryset based on search criteria
####################################
def searchCurriculaTiles(request, queryset, search_criteria):
  query_filter = Q()

  base_filter = Q()
  keyword_filter = None
  subject_filter = None
  curricula_type_filter = None
  status_filter = None
  teacher_authored_filter = None
  my_curricula_filter =  None
  favorite_curricula_filter = None
  shared_curricula_filter = None
  search_units = True

  if search_criteria:
    if 'keywords' in search_criteria and search_criteria['keywords'][0] != '':

      keywords = search_criteria['keywords'][0]
      #keyword search for units and standalone curricula
      keyword_filter = Q(title__icontains=keywords) | Q(time__icontains=keywords)
      keyword_filter = keyword_filter | (Q(curriculumcollaborator__user__first_name__icontains=keywords) & Q(curriculumcollaborator__privilege='E'))
      keyword_filter = keyword_filter | (Q(curriculumcollaborator__user__last_name__icontains=keywords) & Q(curriculumcollaborator__privilege='E'))
      keyword_filter = keyword_filter | Q(taxonomy__title__icontains=keywords)
      keyword_filter = keyword_filter | Q(taxonomy__category__name__icontains=keywords)
      keyword_filter = keyword_filter | Q(taxonomy__category__standard__name__icontains=keywords)
      keyword_filter = keyword_filter | Q(level__icontains=keywords)
      keyword_filter = keyword_filter | Q(subject__name__icontains=keywords)

    if 'subjects' in search_criteria:
      #subjects = map(int, search_criteria['subjects'])
      subjects = [int(i) for i in search_criteria['subjects']]
      subject_filter = Q(subject__id__in=subjects)

    if 'curricula_types' in search_criteria:
      curricula_types = search_criteria['curricula_types']
      curricula_type_filter = Q(curriculum_type__in=curricula_types)
      if 'U' not in curricula_types:
        search_units = False

    if 'status' in search_criteria:
      status = search_criteria['status']
      status_filter = Q(status__in=status)
    else:
      if not hasattr(request.user, 'administrator'):
        status_filter = ~Q(status='R')

    if keyword_filter:
      base_filter = base_filter & keyword_filter
    if subject_filter:
      base_filter = base_filter & subject_filter
    if curricula_type_filter:
      base_filter = base_filter & curricula_type_filter
    if status_filter:
      base_filter = base_filter & status_filter

    if 'buckets' in search_criteria:
      buckets = search_criteria['buckets']
      if 'teacher_authored' in buckets:
        #teacher authored units and standalone curricula
        teacher_authored_filter = Q(curriculumcollaborator__user__teacher__isnull=False)
        teacher_authored_filter = base_filter & teacher_authored_filter
        query_filter = query_filter | teacher_authored_filter

      if 'my_curricula' in buckets:
        #my unit and standalone curricula
        my_curricula_filter = (Q(curriculumcollaborator__user=request.user) & Q(curriculumcollaborator__privilege='E'))
        my_curricula_filter = base_filter & my_curricula_filter
        query_filter = query_filter | my_curricula_filter

      if 'favorite_curricula' in buckets:
        favorite_curricula_filter = (Q(bookmarked__teacher=request.user.teacher))
        favorite_curricula_filter = base_filter & favorite_curricula_filter
        query_filter = query_filter | favorite_curricula_filter

      if 'shared_curricula' in buckets:
        #shared unit and standalone curricula
        shared_curricula_filter = (Q(curriculumcollaborator__user=request.user) & Q(curriculumcollaborator__privilege='V'))
        shared_curricula_filter = base_filter & shared_curricula_filter
        query_filter = query_filter | shared_curricula_filter

    #no bucket/collection selected
    else:
      if request.user.is_anonymous or hasattr(request.user, 'student') or hasattr(request.user, 'school_administrator'):
        query_filter = base_filter & Q(status='P')
      elif hasattr(request.user, 'teacher'):
        query_filter = Q(curriculumcollaborator__user=request.user) | Q(bookmarked__teacher=request.user.teacher)
        query_filter = query_filter | Q(status='P')
        query_filter = base_filter & query_filter
      elif hasattr(request.user, 'researcher'):
        query_filter = Q(curriculumcollaborator__user=request.user) | Q(status='P')
        query_filter = base_filter & query_filter
      else:
        query_filter = base_filter

  #no filter provided
  else:
    if request.user.is_anonymous or hasattr(request.user, 'student') or hasattr(request.user, 'school_administrator'):
        query_filter = Q(status='P')
    elif hasattr(request.user, 'teacher'):
      query_filter = Q(curriculumcollaborator__user=request.user) | Q(bookmarked__teacher=request.user.teacher)
      query_filter = query_filter | Q(status='P')

    elif hasattr(request.user, 'researcher'):
      query_filter = Q(curriculumcollaborator__user=request.user) | Q(status='P')

  raw_result = queryset.filter(query_filter)
  if search_units:
    units = raw_result.values_list('unit', flat=True).distinct()
    filtered_result = queryset.filter(Q(Q(unit__isnull=True), query_filter) | Q(id__in=units)).distinct()
  else:
    filtered_result = queryset.filter(Q(unit__isnull=True), query_filter).distinct()
  return filtered_result
####################################
# BULK ACTION FOR ALL MODELS
####################################
@login_required
def _do_action(request, id_list, model, object_id=None):
  action_params = request.POST
  if '' == action_params.get('action') or len(id_list) == 0:
    return True
  if model == 'user' or model == 'student':
    if model == 'user':
      users = User.objects.filter(id__in=id_list)
    elif model == 'student':
      users = User.objects.filter(student__id__in=id_list)

    if 'delete_selected' == action_params.get('action'):
      for user in users:
        transferCurriculum(request, user)
      users.delete()
      messages.success(request, "Selected user(s) deleted.")
      return True
    if 'remove_selected' == action_params.get('action'):
      for user in users:
        removeStudent(request, object_id, user.student.id)
      messages.success(request, "Selected student(s) removed from class.")
      return True
    elif 'activate_selected' == action_params.get('action'):
      for user in users:
        user.is_active = True
        user.save()
      messages.success(request, "Selected user(s) activated.")
      return True
    elif 'inactivate_selected' == action_params.get('action'):
      for user in users:
        user.is_active = False
        user.save()
      messages.success(request, "Selected user(s) inactivated.")
      return True
    elif u'school_selected' == action_params.get(u'action'):
      if u'subaction' in action_params:
        school_id = action_params.get(u'subaction')
        school = models.School.objects.get(id=school_id)
        for user in users:
          if hasattr(user, 'school_administrator'):
            school_admin = models.SchoolAdministrator.objects.get(user=user)
            update_school(request, school_admin, school)
          elif hasattr(user, 'teacher'):
            teacher = models.Teacher.objects.get(user=user)
            update_school(request, teacher, school)
          elif hasattr(user, 'student'):
            student = models.Student.objects.get(user=user)
            update_school(request, student, school)
        messages.success(request, "Selected users' school updated.")
        return True
      else:
        return False
  elif model == 'group':
    groups = models.UserGroup.objects.filter(id__in=id_list)
    if 'activate_selected' == action_params.get('action'):
      groups.update(is_active=True)
      print('activation done')
      messages.success(request, "Selected class(es) activated.")
      return True
    elif 'inactivate_selected' == action_params.get('action'):
      groups.update(is_active=False)
      #archive assignments
      archiveAssignmentsByClass(request, id_list)
      messages.success(request, "Selected class(es) inactivated.")
      return True
  else:
    return False

####################################
# Update school for the given user.
# If the user is a teacher, also update the
# school of students associated via group
####################################
def update_school(request, user, school):

  if isinstance(user, models.SchoolAdministrator):
    user.school = school
    user.save()
  elif isinstance(user, models.Teacher):
    user.school = school
    user.save()
    #find all the groups this teacher owns
    groups = models.UserGroup.objects.all().filter(teacher=user)
    for group in groups:
      for membership in group.group_members.all():
        student = models.Student.objects.get(id=membership.student.id)
        student.school = school
        student.save()
  elif isinstance(user, models.Student):
    user.school = school
    user.save()

####################################
# CREATE MODIFY A RESERCH CATEGORY
####################################
@login_required
def research_category(request, id=''):
  try:
    # check if the user has permission to create or modify a lesson
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to modify this research category</h1>')

    # check if the research category exists
    if '' != id:
      category = models.ResearchCategory.objects.get(id=id)
    else:
      category = models.ResearchCategory()

    if request.method == 'GET':
        form = forms.ResearchCategoryForm(instance=category, prefix='category')
        context = {'form': form,}
        return render(request, 'ctstem_app/ResearchCategory.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      form = forms.ResearchCategoryForm(data, instance=category, prefix="category")
      if form.is_valid():
        form.save()
        messages.success(request, "Research Category Saved.")
        return shortcuts.redirect('ctstem:categories',)
      else:
        print(form.errors)
        messages.error(request, "The research category could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form}
        return render(request, 'ctstem_app/ResearchCategory.html', context)

  except models.ResearchCategory.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested Research Category not found</h1>')

####################################
# RESEARCH CATEGORIES TABLE VIEW
####################################
def research_categories(request):
  categories = models.ResearchCategory.objects.all()
  context = {'categories': categories}
  return render(request, 'ctstem_app/ResearchCategories.html', context)

####################################
# DELETE RESEARCH CATEGORY
####################################
def deleteCategory(request, id=''):
  try:
    # check if the user has permission to delete a category
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to delete this category</h1>')
    # check if the lesson exists
    if '' != id:
      category = models.ResearchCategory.objects.get(id=id)
    else:
      raise models.ResearchCategory.DoesNotExist

    if request.method == 'GET' or request.method == 'POST':

      category.delete()
      messages.success(request, '%s deleted' % category.category)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.ResearchCategory.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested category not found</h1>')

####################################
# PUBLICATIONS TABLE VIEW
####################################
def publications(request):
  publications = models.Publication.objects.all().order_by('order')
  context = {'publications': publications}
  return render(request, 'ctstem_app/Publications.html', context)

####################################
# CREATE MODIFY A PUBLICATION
####################################
@login_required
def publication(request, id=''):
  try:
    # check if the user has permission to create or modify a lesson
    if hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to modify this publication</h1>')
    # check if the lesson exists
    if '' != id:
      publication = models.Publication.objects.get(id=id)
    else:
      publication = models.Publication()

    if request.method == 'GET':
        form = forms.PublicationForm(instance=publication, prefix='publication')
        context = {'form': form,}
        return render(request, 'ctstem_app/Publication.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      form = forms.PublicationForm(data, instance=publication, prefix="publication")
      if form.is_valid():
        savedPublication = form.save(commit=False)
        savedPublication.save()
        form.save()
        reorder_publications(request)
        messages.success(request, "Publication Saved.")
        return shortcuts.redirect('ctstem:publications',)
      else:
        print(form.errors)
        messages.error(request, "The publication could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form}
        return render(request, 'ctstem_app/Publication.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Publication.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested publication not found</h1>')


####################################
# DELETE PUBLICATION
####################################
def deletePublication(request, id=''):
  try:
    # check if the user has permission to delete a lesson
    if hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to delete this publication</h1>')
    # check if the lesson exists
    if '' != id:
      publication = models.Publication.objects.get(id=id)
    else:
      raise models.Publication.DoesNotExist

    if request.method == 'GET' or request.method == 'POST':

      publication.delete()
      messages.success(request, 'Publication deleted')
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Publication.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested publication not found</h1>')


####################################
# GROUPS TABLE VIEW
####################################
@login_required
def groups(request, status='active'):
  if request.method == 'GET' or request.method == 'POST':
    search_criteria = None
    if request.method == 'POST':
      data = request.POST.copy()
      id_list = []
      for key in data:
        if 'group_' in key:
          id_list.append(data[key])
      _do_action(request, id_list, 'group')
      #search
      if 'search_criteria' in data:
        search_criteria = data['search_criteria']
      searchForm = forms.SearchForm(data)
    else:
      searchForm = forms.SearchForm()

    is_active = True
    active_group_count = 0
    active_group_students = 0
    active_group_assignments = 0
    if status == 'inactive':
      is_active = False
    if hasattr(request.user, 'administrator') or hasattr(request.user, 'researcher'):
      groups = models.UserGroup.objects.all().filter(is_active=is_active)
    elif hasattr(request.user, 'school_administrator'):
      groups = models.UserGroup.objects.all().filter(is_active=is_active, teacher__school=request.user.school_administrator.school)
    elif hasattr(request.user, 'teacher'):
      total_groups = models.UserGroup.objects.all().filter(Q(teacher=request.user.teacher) | Q(shared_with=request.user.teacher)).distinct()
      active_groups = total_groups.filter(is_active=True)
      active_group_count = active_groups.count()
      if is_active == True:
        if total_groups.count() == 0:
          new_group = models.UserGroup(title='My Class 1', teacher=request.user.teacher, is_active=True)
          new_group.save()
          active_group_count = 1
      active_group_students = models.Membership.objects.all().filter(group__in=active_groups).values('student').distinct().count()
      active_group_assignments = models.Assignment.objects.all().filter(group__in=active_groups).distinct().count()
      groups = models.UserGroup.objects.all().filter(Q(is_active=is_active), Q(teacher=request.user.teacher) | Q(shared_with=request.user.teacher)).distinct()

    else:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to view classes</h1>')

    if search_criteria:
      groups = searchGroups(request, groups, search_criteria)

    order_by = request.GET.get('order_by') or 'title'
    direction = request.GET.get('direction') or 'asc'
    ignorecase = request.GET.get('ignorecase') or 'false'
    sort_order = [{'order_by': order_by, 'direction': direction, 'ignorecase': ignorecase}]
    group_list = paginate(request, groups, sort_order, 25)

    current_site = Site.objects.get_current()
    domain = current_site.domain
    uploadForm = forms.UploadFileForm(user=request.user)
    assignmentForm = forms.AssignmentSearchForm(user=request.user)
    context = {'groups': group_list, 'role':'groups', 'uploadForm': uploadForm,
               'group_status': status, 'domain': domain, 'assignmentForm': assignmentForm,
               'searchForm': searchForm, 'order_by': order_by, 'direction': direction,
               'active_group_count': active_group_count,
               'active_group_students': active_group_students,
               'active_group_assignments': active_group_assignments}
    return render(request, 'ctstem_app/UserGroups.html', context)

  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# CREATE MODIFY A USER GROUP
####################################
@login_required
def group(request, id=''):
  try:
    # check if the user has permission to create or modify a group
    group = None
    if '' != id:
      has_permission = check_group_permission(request, id)
      if has_permission:
        group = models.UserGroup.objects.get(id=id)
      else:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to view/modify this class</h1>')
    else:
      if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'school_administrator') == False and hasattr(request.user, 'teacher') == False:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to create/modify a class</h1>')
      else:
        group = models.UserGroup()

    if request.method in ['GET', 'POST']:
      assignments = {}
      keys = []
      for assignment in models.Assignment.objects.all().filter(group=group).order_by('curriculum__unit__title', 'curriculum__order'):
        instances = models.AssignmentInstance.objects.all().filter(assignment=assignment)
        curriculum = assignment.curriculum

        if curriculum.curriculum_type in ['L', 'A'] and curriculum.unit is not None:
          key = curriculum.unit
        else:
          key = curriculum

        if key not in keys:
          keys.append(key)

        if key in assignments:
          assignments[key][curriculum.order] = assignment
        else:
          assignments[key] = {curriculum.order: assignment}

      keys.sort(key=lambda x:x.title)
      uploadForm = forms.UploadFileForm(user=request.user)
      assignmentForm = forms.AssignmentSearchForm(user=request.user)
      studentAddForm = forms.StudentAddForm()

      if request.method == 'GET':
        form = forms.UserGroupForm(user=request.user, instance=group, prefix='group')
        context = {'form': form, 'role': 'group', 'uploadForm': uploadForm, 'assignmentForm': assignmentForm, 'studentAddForm': studentAddForm, 'assignments': assignments, 'keys': keys}

        return render(request, 'ctstem_app/UserGroup.html', context)

      elif request.method == 'POST':
        data = request.POST.copy()
        form = forms.UserGroupForm(user=request.user, data=data, files=request.FILES, instance=group, prefix="group")

        if form.is_valid():
          savedGroup = form.save()
          #if group is being inactivated, archive the associated assignments
          if 'group-is_active' not in data:
            archiveAssignmentsByClass(request, [id])

          id_list = []
          for key in data:
            if 'student_' in key:
              id_list.append(data[key])
          _do_action(request, id_list, 'student', id)
          messages.success(request, "Class Saved.")
          return shortcuts.redirect('ctstem:group', id=savedGroup.id)
        else:
          print(form.errors)
          messages.error(request, "The class could not be saved because there were errors.  Please check the errors below.")
          context = {'form': form, 'role': 'group', 'uploadForm': uploadForm, 'assignmentForm': assignmentForm, 'studentAddForm': studentAddForm, 'assignments': assignments, 'keys': keys}

        return render(request, 'ctstem_app/UserGroup.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.UserGroup.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested class not found</h1>')

####################################
# Search Assignment
####################################
@login_required
def searchAssignment(request):
  # check if the user has permission to search and assign curriculum
  if hasattr(request.user, 'school_administrator') == False and hasattr(request.user, 'teacher') == False and  hasattr(request.user, 'administrator') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege search assignments</h1>')

  if 'POST' == request.method:
    data = request.POST.copy()
    curricula = []
    if data['group']:
      query_filter = {}
      if data['curriculum_type']:
        query_filter['curriculum_type'] = str(data['curriculum_type'])
      else:
        query_filter['curriculum_type__in'] = ['U', 'L']

      query_filter['unit__isnull'] = True

      if data['title']:
        query_filter['title__icontains'] = str(data['title'])
      if data['subject']:
        query_filter['subject__id'] = data['subject']


      curriculumQueryset = models.Curriculum.objects.filter(**query_filter).order_by(Lower('title'))

      for curriculum in curriculumQueryset:
        if check_curriculum_permission(request, curriculum.id, 'assign'):
          curr = {'id': curriculum.id, 'curriculum_type': curriculum.get_curriculum_type_display(), 'title': curriculum.title, 'subject': [subject.name for subject in curriculum.subject.all()]}

          if curriculum.curriculum_type == 'U':
            underlying_curriculum_queryset = underlyingCurriculum(request, 'assign', curriculum.id)
            underlying_curriculum = []
            unit_assigned = False
            curriculum_assigned_count = 0
            for und_curr in underlying_curriculum_queryset:
              curr_assigned = False
              assignments = models.Assignment.objects.all().filter(curriculum=und_curr, group__id=int(data['group']))
              if assignments.count() > 0:
                curr_assigned = True
                curriculum_assigned_count = curriculum_assigned_count + 1
              underlying_curriculum.append({'id': und_curr.id, 'order': und_curr.order, 'title': und_curr.title, 'assigned': curr_assigned, 'curriculum_type': und_curr.get_curriculum_type_display()})

            curr['assigned'] = len(underlying_curriculum_queryset) == curriculum_assigned_count
            curr['underlying_curriculum'] = underlying_curriculum
            curr['underlying_curriculum_count'] = len(underlying_curriculum_queryset)
            curr['underlying_curriculum_assigned'] = curriculum_assigned_count
          else:
            assigned = False
            assignments = models.Assignment.objects.all().filter(curriculum=curriculum, group__id=int(data['group']))
            if assignments.count() > 0:
              assigned = True

            curr['assigned'] = assigned
            curr['underlying_curriculum'] = None

          curricula.append(curr)

    context = {'curricula': curricula, 'group_id': data['group'] }
    html = render_to_string('ctstem_app/AssignmentSearchResult.html', context, request)
    return http.HttpResponse(html)

  return http.HttpResponseNotAllowed(['POST'])

####################################
# Get underlying lessons when assigning or previewing
####################################
def underlyingCurriculum(request, action, id=''):

  if request.method == 'GET' or request.method == 'POST':
    curriculum = models.Curriculum.objects.get(id=id)
    underlying_curriculum =  curriculum.underlying_curriculum.all().order_by('order').distinct()
    filtered_curriculum = []
    for curr in underlying_curriculum:
      has_permission = check_curriculum_permission(request, curr.id, action)
      if has_permission:
        filtered_curriculum.append(curr)

    #curriculum_list = [{'id': curr.id, 'title': curr.title} for curr in filtered_curriculum]
    return filtered_curriculum
  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# Get underlying lessons to display on
# the curricula page
####################################
def underlyingCurriculumTable(request, id=''):
  if 'GET' == request.method:
    curriculum = models.Curriculum.objects.get(id=id)
    action = 'preview'
    underlying_curriculum = underlyingCurriculum(request, action, id)
    context = {'underlying_curriculum': underlying_curriculum}
    html = render_to_string('ctstem_app/UnderlyingCurricula.html', context, request)
    return http.HttpResponse(html)

  return http.HttpResponseNotAllowed(['GET'])

####################################
# DELETE A USER GROUP
####################################
@login_required
def deleteGroup(request, id=''):
  try:
    # check if the group exists
    if '' != id:
      group = models.UserGroup.objects.get(id=id)
      # check if the user has permission to delete this group
      privilege = 0
      if hasattr(request.user, 'administrator'):
        privilege = 1

      if privilege == 0:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to delete this class</h1>')

      if request.method == 'GET' or request.method == 'POST':
        group.delete()
        messages.success(request, '"%s" and all related assignments deleted' % group.title)
        return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
      raise models.UserGroup.DoesNotExist

  except models.UserGroup.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested class not found</h1>')

####################################
# Group Dashboard
####################################
@login_required
def groupDashboard(request, id='', curriculum_status='active'):
  try:
    if request.method == 'GET':
      group = models.UserGroup.objects.get(id=id)
      if hasattr(request.user, 'researcher'):
        has_permission = True
      else:
        has_permission = check_group_permission(request, id)

      if not has_permission:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to view this class</h1>')

      assignments = {}
      serial = 0
      status_map = {'N': 'New', 'P': 'In Progress', 'S': 'Submitted', 'F': 'Feedback Ready', 'A': 'Archived'}
      status_color = {'N': 'gray', 'P': 'blue', 'S': 'green', 'F': 'orange', 'A': 'black'}
      students = group.members.all()
      keys = []

      for assignment in models.Assignment.objects.all().filter(group=group).order_by('curriculum__unit__title', 'curriculum__order'):
        instances = models.AssignmentInstance.objects.all().filter(assignment=assignment)
        curriculum = models.Curriculum.objects.get(id=assignment.curriculum.id)
        if (curriculum_status == 'active' and curriculum.status in ['D', 'P']) or (curriculum_status == 'archived' and curriculum.status == 'A'):
          assignment_status = {}
          status = []
          for student in students:
            try:
              instance = instances.get(student=student)
              if instance.status in assignment_status:
                assignment_status[instance.status] +=1
              else:
                assignment_status[instance.status] =1
            except models.AssignmentInstance.DoesNotExist:
              if 'N' in assignment_status:
                assignment_status['N'] +=1
              else:
                assignment_status['N'] =1
          for key, value in list(assignment_status.items()):
            status.append({'name': status_map[key], 'y': value, 'color': status_color[key]})
          serial += 1

          if curriculum.unit is not None:
           key = curriculum.unit
          else:
            key = curriculum

          if key not in keys:
            keys.append(key)

          if key in assignments:
            assignments[key][curriculum.order] = {'assignment': assignment, 'status': status, 'serial': serial}
          else:
            assignments[key] = {curriculum.order : {'assignment': assignment, 'status': status, 'serial': serial}}

      keys.sort(key=lambda x:x.title)
      context = {'group': group, 'assignments': assignments, 'keys': keys, 'curriculum_status': curriculum_status}
      return render(request, 'ctstem_app/GroupDashboard.html', context)

    return http.HttpResponseNotAllowed(['GET'])

  except models.UserGroup.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested class not found</h1>')

####################################
# Assignment Dashboard
####################################
@login_required
def assignmentDashboard(request, id=''):
  try:
    if request.method == 'GET':
      assignment = models.Assignment.objects.get(id=id)
      group = assignment.group

      if hasattr(request.user, 'researcher'):
        has_permission = True
      else:
        has_permission = check_group_permission(request, group.id)

      if not has_permission:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to view this assignment</h1>')

      students = assignment.group.members.all().order_by(Lower('user__last_name'), Lower('user__first_name'))
      questions = models.CurriculumQuestion.objects.all().filter(step__curriculum=assignment.curriculum).order_by('step__order', 'order')
      #for researchers filter out students who have opted out
      if hasattr(request.user, 'researcher'):
        students = students.filter(consent='A')

      instances = models.AssignmentInstance.objects.all().filter(assignment=assignment)
      student_assignment_details = []
      serial = 1

      for student in students:
        try:
          instance = instances.get(student=student)
          total_questions = models.CurriculumQuestion.objects.all().filter(step__curriculum=assignment.curriculum).count()
          attempted_questions = models.QuestionResponse.objects.all().filter(step_response__instance=instance).exclude(response__exact='', response_file__isnull=True).count()
          total_steps = instance.assignment.curriculum.steps.count()
          last_step = instance.last_step
          if total_questions > 0:
            percent_complete = float(attempted_questions)/float(total_questions)*100
          else:
            percent_complete = float(last_step)/float(total_steps)*100

        except models.AssignmentInstance.DoesNotExist:
          instance = None
          percent_complete = 0

        student_assignment_details.append({'serial': serial, 'student': student, 'instance': instance, 'percent_complete': percent_complete})
        serial += 1

      context = {'assignment': assignment, 'student_assignment_details': student_assignment_details, 'question_details': questions}
      return render(request, 'ctstem_app/AssignmentDashboard.html', context)

    return http.HttpResponseNotAllowed(['GET'])

  except models.Assignment.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assignment not found</h1>')

####################################
# STUDENT ASSIGNMENTS
####################################
@login_required
def assignments(request, bucket=''):
  try:
    if hasattr(request.user, 'student') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to view assignments</h1>')

    student = request.user.student
    if request.method == 'GET' or request.method == 'POST':
      groups = models.Membership.objects.all().filter(student=student).values_list('group', flat=True)
      #for each group
      tomorrow = datetime.date.today() + datetime.timedelta(days=1)
      assignments = models.Assignment.objects.all().filter(group__in=groups, assigned_date__lt=tomorrow).order_by('curriculum__unit__title', 'curriculum__order')
      assignment_list = []
      active_list = []
      archived_list = []
      new_count = 0
      serial = 1
      status_list = {'N': 1, 'P': 2, 'S': 3, 'F': 4, 'A': 5}
      for assignment in assignments:
        title = assignment.curriculum.unit.title if assignment.curriculum.unit is not None else assignment.curriculum.title
        try:
          instance = models.AssignmentInstance.objects.get(assignment=assignment, student=student)
          total_questions = models.CurriculumQuestion.objects.all().filter(step__curriculum=assignment.curriculum).count()
          attempted_questions = models.QuestionResponse.objects.all().filter(step_response__instance=instance).exclude(response__exact='', response_file__isnull=True).count()
          total_steps = instance.assignment.curriculum.steps.count()
          last_step = instance.last_step
          percent_complete = 0
          if total_questions > 0:
            percent_complete = float(attempted_questions)/float(total_questions)*100
          elif total_steps > 0:
            percent_complete = float(last_step)/float(total_steps)*100

          if instance.status in ['N', 'P', 'S', 'F']:
            active_list.append({'serial': serial, 'title': title, 'assignment': assignment, 'instance': instance, 'status': status_list[instance.status], 'percent_complete': percent_complete, 'modified_date': instance.modified_date})
          else:
            archived_list.append({'serial': serial, 'title': title, 'assignment': assignment, 'instance': instance, 'status': status_list[instance.status], 'percent_complete': percent_complete, 'modified_date': instance.modified_date})
        except models.AssignmentInstance.DoesNotExist:
          if assignment.group.is_active:
            #only display new assignments for active groups
            instance = None
            new_count += 1
            status = 'N'
            percent_complete = 0
            active_list.append({'serial': serial, 'title': title, 'assignment': assignment, 'instance': instance, 'status': status_list[status], 'percent_complete': percent_complete, 'modified_date': timezone.now()})

        serial += 1

      if bucket == 'inbox':
        assignment_list = active_list
      else:
        assignment_list = archived_list

      if request.method == 'GET':
        sort_by = 'assigned'
        sort_form = forms.InboxSortForm()
      else:
        data = request.POST.copy()
        sort_by = data['sort_by']
        sort_form = forms.InboxSortForm(data)

      # print sort_by
      # if sort_by == 'assigned':
      #   assignment_list.sort(key=lambda item:item['assignment'].assigned_date)
      # elif sort_by == 'group':
      #   assignment_list.sort(key=lambda item:item['assignment'].group)
      # elif sort_by == 'status':
      #   assignment_list.sort(key=lambda item:item['status'])
      # elif sort_by == 'percent':
      #   assignment_list.sort(key=lambda item:item['percent_complete'])
      # elif sort_by == 'modified':
      #   assignment_list.sort(key=lambda item:item['modified_date'])
      assignment_list.sort(key=lambda item:item['title'].lower())

      context = {'assignment_list': assignment_list, 'new': new_count, 'inbox': len(active_list), 'archived': len(archived_list), 'sort_form': sort_form, 'consent': student.consent}
      return render(request, 'ctstem_app/MyAssignments.html', context)
    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Student.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested student not found</h1>')

####################################
# STUDENT archives assignment
####################################
@login_required
def archiveAssignment(request, instance_id=''):
  try:
    instance = models.AssignmentInstance.objects.get(id=instance_id)
    if hasattr(request.user, 'student') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to archive this assignments</h1>')
    elif request.user.student != instance.student:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to archive this assignments</h1>')

    if instance.status == 'F':
      instance.status = 'A'
      instance.save()
      messages.success(request, 'Your assignment has been archived')
    else:
      messages.success(request, 'Only assignments with status Feedback Ready can be archived')

    return shortcuts.redirect('ctstem:assignments', bucket='inbox')

  except models.AssignmentInstance.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assignment not found</h1>')


####################################
# Inactivate a group and
# archive the associated assignments
####################################
def inactivateGroup(request, id=''):
  try:
    privilege = 0
    if '' != id:
      group = models.UserGroup.objects.get(id=id)
      if hasattr(request.user, 'administrator') or hasattr(request.user, 'researcher'):
        privilege = 1
      elif hasattr(request.user, 'school_administrator'):
        if group.is_active and group.teacher.school == request.user.school_administrator.school:
          privilege = 1
      elif hasattr(request.user, 'teacher'):
        if group.is_active and group.teacher == request.user.teacher:
          privilege = 1

      if privilege > 0:
        group.is_active = False
        group.save()
        messages.success(request, '"%s" inactivated' % group.title)
        archiveAssignmentsByClass(request, [id])
        return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))
      else:
        http.HttpResponseNotFound('<h1>You do not have the privilege to inactivate this class</h1>')
    else:
      raise models.UserGroup.DoesNotExist
  except models.UserGroup.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested class not found</h1>')

####################################
# When group is inactivated by an Admin or a Teacher,
# archive the associated assignments
####################################
def archiveAssignmentsByClass(request, group_ids):
  groups = models.UserGroup.objects.filter(id__in=group_ids)
  #get all assignments for the groups
  instances = models.AssignmentInstance.objects.all().filter(assignment__group__in=groups)
  instances.update(status= 'A')
  messages.success(request, 'All associated assignments have been archived')

####################################
# When a curriculum is Archived,
# archive all the associated assignments
####################################
def archiveAssignmentsByCurriculum(request, curriculum_id):
  #get all assignments for the curriculu,
  instances = models.AssignmentInstance.objects.all().filter(assignment__curriculum__id=curriculum_id)
  instances.update(status= 'A')
  messages.success(request, 'All associated assignments have been archived')

####################################
# STUDENT ATTEMPTING ASSIGNMENTS
####################################
@login_required
def assignment(request, assignment_id='', instance_id='', step_order=''):
  try:
    if hasattr(request.user, 'student') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to do this assignments</h1>')

    print(assignment_id, instance_id, step_order)
    assignment = models.Assignment.objects.get(id=assignment_id)
    curriculum = assignment.curriculum

    #resuming/viewing assignment
    if '' != instance_id:
      instance = models.AssignmentInstance.objects.get(assignment__id=assignment_id, id=instance_id, student=request.user.student)
      if request.user.student != instance.student:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to do this assignments</h1>')
      last_step = instance.last_step
      #prevent users from manipulating the url in the browser for new and in progress assignments
      if int(step_order) > last_step + 1 and instance.status in ('N', 'P'):
        messages.error(request, 'Please use the buttons below to navigate between steps')
        return shortcuts.redirect('ctstem:resumeAssignment', assignment_id=assignment_id, instance_id=instance.id, step_order=last_step)

    #starting a new assignment or retrieve an existing assignment
    else:
      instance, created = models.AssignmentInstance.objects.get_or_create(assignment=assignment, student=request.user.student)
      step_order = 0

    if 'GET' == request.method or 'POST' == request.method:
      steps = models.Step.objects.all().filter(curriculum=curriculum)
      total_steps = steps.count()
      if int(step_order) == 0:
        attachments = models.Attachment.objects.all().filter(Q(curriculum=curriculum) | Q(curriculum=curriculum.unit), teacher_only=False)
        context = {'curriculum': curriculum, 'instance': instance, 'total_steps': total_steps, 'step_order': step_order, 'attachments': attachments}
        return render(request, 'ctstem_app/AssignmentStep.html', context)
      else:
        step = steps.get(order=step_order)
        #create step response object
        assignmentStepResponse, created = models.AssignmentStepResponse.objects.get_or_create(instance=instance, step=step)
        curriculumQuestions = models.CurriculumQuestion.objects.all().filter(step=step).order_by('order')
        #create notes object
        notes, created = models.AssignmentNotes.objects.get_or_create(instance=instance)

        #create empty question responses if one does not exist
        for curriculumQuestion in curriculumQuestions:
          questionResponse, created = models.QuestionResponse.objects.get_or_create(step_response=assignmentStepResponse, curriculum_question=curriculumQuestion)
          if questionResponse.response is None:
            questionResponse.response = ''
            questionResponse.save()

        if 'GET' == request.method:
          #get the assignment step
          form = forms.AssignmentStepResponseForm(instance=assignmentStepResponse, prefix="step_response")
          questionResponseFormset = nestedformset_factory(models.AssignmentStepResponse, models.QuestionResponse, form=forms.QuestionResponseForm,
                                                    nested_formset=inlineformset_factory(models.QuestionResponse, models.QuestionResponseFile, form=forms.QuestionResponseFileForm, can_delete=True, extra=2),
                                                    can_delete=False, can_order=True, extra=0)

          #questionResponseFormset=inlineformset_factory(models.AssignmentStepResponse, models.QuestionResponse, form=forms.QuestionResponseForm, can_delete=False, can_order=True, extra=extra)
          formset = questionResponseFormset(instance=assignmentStepResponse, prefix='form')

          if int(step_order) == 1 and assignment.curriculum.curriculum_type == 'L':
            instanceform = forms.AssignmentInstanceForm(assignment=assignment, instance=instance, prefix="teammates")
          else:
            instanceform = None

          notesform = forms.AssignmentNotesForm(instance=notes, prefix="notes")

          context = {'curriculum': curriculum, 'instance': instance, 'instanceform': instanceform, 'notesform': notesform, 'form': form, 'formset': formset, 'total_steps': total_steps, 'step_order': step_order}
          return render(request, 'ctstem_app/AssignmentStep.html', context)

        elif 'POST' == request.method:
          data = request.POST.copy()
          #is this a save or a submit
          #print data
          save_only = int(data['save'])
          form = forms.AssignmentStepResponseForm(data=data, instance=assignmentStepResponse, prefix="step_response")
          #questionResponseFormset=inlineformset_factory(models.AssignmentStepResponse, models.QuestionResponse, form=forms.QuestionResponseForm, can_delete=False, can_order=True, extra=0)
          questionResponseFormset = nestedformset_factory(models.AssignmentStepResponse, models.QuestionResponse, form=forms.QuestionResponseForm,
                                                    nested_formset=inlineformset_factory(models.QuestionResponse, models.QuestionResponseFile, form=forms.QuestionResponseFileForm, can_delete=True, extra=2),
                                                    can_delete=False, can_order=True, extra=0)
          formset = questionResponseFormset(data, request.FILES, instance=assignmentStepResponse, prefix='form')

          if int(step_order) == 1 and assignment.curriculum.curriculum_type == 'L':
            instanceform = forms.AssignmentInstanceForm(data=data, assignment=assignment, instance=instance, prefix="teammates")
          else:
            instanceform = None

          notesform = forms.AssignmentNotesForm(data=data, instance=notes, prefix="notes")

          if form.is_valid() and formset.is_valid():
            if save_only == 1 or step.order < total_steps:
              instance.status = 'P'
              # if submit then increase the last step completed counter
              if save_only == 0:
                instance.last_step = step.order
              # if save then set the last step completed to the previous step
              else:
                instance.last_step = step.order - 1
            else:
              instance.status = 'S'
              instance.last_step = step.order

            #find the delta between the last save and current time and update the instance
            last_save = instance.modified_date
            current_time = datetime.datetime.now(timezone.utc)
            delta = current_time - last_save
            old_time_spent = instance.time_spent
            new_time_spent = old_time_spent + delta.total_seconds()
            instance.time_spent = new_time_spent
            instance.save()

            if instanceform and instanceform.is_valid():
              instanceform.save()

            #save notes form
            if notesform.is_valid():
              notesform.save()

            #save assignment step response
            assignmentStepResponse.save()

            questionCount = 0
            if request.is_ajax():
              formset.save(commit=False)
              questionResponses = {}
              # get the question response ids to update the front end
              for questionform in formset:
                questionCount = questionCount + 1
                if questionform.instance.curriculum_question.question.answer_field_type != 'FI':
                  questionResponse = questionform.save()
                else:
                  questionform.instance.save()
                #print 'question order ', questionform.instance.curriculum_question.order
                questionResponses['id_form-%d-id'%(questionform.instance.curriculum_question.order-1)] = questionform.instance.id
            else: # non ajax post
              formset.save()

            #update the instance
            #submission
            if instance.status == 'S':
              messages.success(request, 'Your assignment has been submitted.  You will not be able to make further changes.')
              return shortcuts.redirect('ctstem:assignments', bucket='inbox')
            else:
              if save_only == 1:
                if not request.is_ajax():
                  messages.success(request, 'Your responses have been saved')
                next_step = step.order
              else:
                messages.success(request, 'Your previous steps have been saved')
                next_step = step.order + 1

              if request.is_ajax():
                url = '/assignment/%s/%s/%s/' % (assignment_id, instance.id, step_order)
                response_data = {'message': 'Your responses were auto saved at %s' % datetime.datetime.now().time().strftime('%r'), 'url': url, 'questionResponses': questionResponses, 'questionCount': questionCount}
                return http.HttpResponse(json.dumps(response_data), content_type = 'application/json')
              else:
                return shortcuts.redirect('ctstem:resumeAssignment', assignment_id=assignment_id, instance_id=instance.id, step_order=next_step)

          else:
            logger.error({'action': 'save assignment', 'user': str(request.user.username),
                          'curriculum': str(curriculum.title.encode('utf-8')), 'step': str(step.title.encode('utf-8')), 'step_order': int(step_order),
                          'assignment_id': int(assignment_id), 'instance_id': int(instance_id),
                          'form errors': str(form.errors),
                          'form non field errors': str(form.non_field_errors),
                          'formset errors': str(formset.errors),
                          'formset non form errors': str(formset.non_form_errors)})

            message = 'Your responses could not be saved. Please correct the errors below and click '
            if save_only == 1:
              message = message + 'Save again.'
            else:
              if int(step_order) == int(total_steps):
                message = message + 'Submit again.'
              else:
                message = message + 'Save & Continue again.'

            messages.error(request, message)

          context = {'curriculum': curriculum, 'instance': instance, 'instanceform': instanceform, 'notesform': notesform, 'form': form, 'formset': formset, 'total_steps': total_steps, 'step_order': step_order}
          return render(request, 'ctstem_app/AssignmentStep.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])
  except models.AssignmentInstance.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assignment not found</h1>')
  except models.Step.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Curriculum Step not found </h1>')

####################################
# Teacher feedback
####################################
@login_required
def feedback(request, assignment_id='', instance_id=''):
  try:

    if '' != instance_id:
      instance = models.AssignmentInstance.objects.get(assignment__id=assignment_id, id=instance_id)
      #get the previous and next student instances
      groupInstances = models.AssignmentInstance.objects.all().filter(assignment__id=assignment_id)
      count = groupInstances.count()
      prevIdx = nextIdx = 0
      prevInstance = nextInstance = None
      for idx, inst in enumerate(groupInstances):
        if instance == inst:
          prevIdx = idx - 1
          nextIdx = idx + 1
      if prevIdx >= 0 and prevIdx < count:
        prevInstance = groupInstances[prevIdx]
      if nextIdx >= 0 and nextIdx < count:
        nextInstance = groupInstances[nextIdx]

      school = instance.student.school
      group = instance.assignment.group
      student = instance.student

      if hasattr(request.user, 'researcher'):
        if student.consent == 'A':
          has_permission = True
        else:
          has_permission = False
      else:
        has_permission = check_group_permission(request, group.id)

      if not has_permission:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to provide feedback on this assignment</h1>')

      feedback, created = models.AssignmentFeedback.objects.get_or_create(instance=instance)
      stepResponses = models.AssignmentStepResponse.objects.all().filter(instance=instance).order_by('step__order')
      for stepResponse in stepResponses:
        stepFeeback, created = models.StepFeedback.objects.get_or_create(assignment_feedback=feedback, step_response=stepResponse)

        questionResponses = models.QuestionResponse.objects.all().filter(step_response=stepResponse).order_by('curriculum_question__order')
        for questionResponse in questionResponses:
          questionFeedback, created = models.QuestionFeedback.objects.get_or_create(step_feedback=stepFeeback, response=questionResponse)

      if 'GET' == request.method:
        form = forms.FeedbackForm(instance=feedback, prefix='feedback')
        #AssessmentStepFormSet = inlineformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,can_delete=True, can_order=True, extra=1)

        StepFeedbackFormSet = nestedformset_factory(models.AssignmentFeedback, models.StepFeedback, form=forms.StepFeedbackForm,
                                                      nested_formset=inlineformset_factory(models.StepFeedback, models.QuestionFeedback, form=forms.QuestionFeedbackForm, can_delete=False, can_order=False, extra=0),
                                                      can_delete=False, can_order=False, extra=0)


        formset = StepFeedbackFormSet(instance=feedback, prefix='form')

        context = {'form': form, 'formset': formset, 'nextInstance': nextInstance, 'prevInstance': prevInstance}
        return render(request, 'ctstem_app/Feedback.html', context)
      elif 'POST' == request.method:
        data = request.POST.copy()

        form = forms.FeedbackForm(data, instance=feedback, prefix='feedback')
        #AssessmentStepFormSet = inlineformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,can_delete=True, can_order=True, extra=1)

        StepFeedbackFormSet = nestedformset_factory(models.AssignmentFeedback, models.StepFeedback, form=forms.StepFeedbackForm,
                                                      nested_formset=inlineformset_factory(models.StepFeedback, models.QuestionFeedback, form=forms.QuestionFeedbackForm, can_delete=False, can_order=False, extra=0),
                                                      can_delete=False, can_order=False, extra=0)


        formset = StepFeedbackFormSet(data, instance=feedback, prefix='form')
        if form.is_valid() and formset.is_valid():
          form.save()
          formset.save()

          if data['save_and_close'] == 'true':
            instance.status = 'F'
            instance.save()
            messages.success(request, 'Your feedback has been saved and sent to the student')
            #notify student via email that feedback is ready
            send_feedback_ready_email(instance.student.user.email, instance.assignment.curriculum)
            #return shortcuts.redirect('ctstem:assignmentDashboard', id=assignment_id)
          else:
            messages.success(request, 'Your feedback has been saved')
        else:
          print(form.errors)
          print(formset.errors)
          messages.error(request, 'Your feedback could not be saved')

        context = {'form': form, 'formset': formset, 'nextInstance': nextInstance, 'prevInstance': prevInstance}
        return render(request, 'ctstem_app/Feedback.html', context)
    else:
      raise models.AssignmentInstance.DoesNotExist

  except models.AssignmentInstance.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assignment not found</h1>')
  except models.Step.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Curriculum Step not found </h1>')

####################################
# Teacher feedback
####################################
@login_required
def question_response_review(request, assignment_id='', curriculum_question_id=''):
  try:
    if '' != assignment_id:
      assignment = models.Assignment.objects.get(id=assignment_id)
      school = assignment.group.teacher.school
      group = assignment.group
      allow_save = False


      if hasattr(request.user, 'researcher'):
        has_permission = True
      else:
        has_permission = check_group_permission(request, group.id)

      if not has_permission:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to review responses for this question</h1>')

      members = group.members

      if hasattr(request.user, 'researcher'):
        members = members.filter(consent='A')

      members = members.order_by(Lower('user__last_name'), Lower('user__first_name'))
      curriculum_question = models.CurriculumQuestion.objects.get(id=curriculum_question_id)
      response_feedback = []
      for member in members:
        try:
          instance = models.AssignmentInstance.objects.get(assignment=assignment, student=member)
          status = instance.status
          question_response = models.QuestionResponse.objects.get(step_response__instance=instance, curriculum_question=curriculum_question)

          feedback = create_feedback_hierarchy(request, instance)
          step_feedback = models.StepFeedback.objects.get(assignment_feedback=feedback, step_response=question_response.step_response)
          question_feedback = models.QuestionFeedback.objects.get(step_feedback=step_feedback, response=question_response)

          if status in ['P', 'S']:
            if question_response.response or question_response.response_file.all():
              question_feedback_form = forms.QuestionFeedbackForm(instance=question_feedback, prefix=question_feedback.id)
              allow_save = True
              message = None
            else:
              question_response = None
              question_feedback_form = None
              message = 'Question not attempted'
          else:
            question_feedback_form = None
            if question_feedback.feedback:
              message = question_feedback.feedback
            else:
              message = 'Feedback not provided'

        except models.AssignmentInstance.DoesNotExist:
          #assignment not started
          question_response = None
          question_feedback_form = None
          message = 'Assignment not started'
          status = 'N'
        except models.QuestionResponse.DoesNotExist:
          #question not attempted
          question_response = None
          question_feedback_form = None
          message = 'Question not attempted'

        response_feedback.append({'student': member, 'question_response': question_response, 'question_feedback_form': question_feedback_form, 'message': message, 'status': status})

      #get the previous and next student instances
      curriculum_questions = models.CurriculumQuestion.objects.all().filter(step__curriculum__id=curriculum_question.step.curriculum.id).order_by('step__order', 'order')
      count = curriculum_questions.count()
      prevIdx = nextIdx = 0
      prevQuestion = nextQuestion = None
      for idx, quest in enumerate(curriculum_questions):
        if curriculum_question == quest:
          prevIdx = idx - 1
          nextIdx = idx + 1
      if prevIdx >= 0 and prevIdx < count:
        prevQuestion = curriculum_questions[prevIdx]
      if nextIdx >= 0 and nextIdx < count:
        nextQuestion = curriculum_questions[nextIdx]

      if 'GET' == request.method:
        context = {'group': group, 'assignment': assignment, 'curriculum_question': curriculum_question, 'response_feedback': response_feedback, 'nextQuestion': nextQuestion, 'prevQuestion': prevQuestion, 'allow_save': allow_save}
        return render(request, 'ctstem_app/QuestionReview.html', context)

      elif 'POST' == request.method:
        data = request.POST.copy()
        feedback_saved = False
        for k, v in data.lists():
          if 'feedback' in k:
            feedback_id = int(k[:k.index('-')])
            question_feedback = models.QuestionFeedback.objects.get(id=feedback_id)
            question_feedback.feedback = v[0]
            question_feedback.save()
            feedback_saved = True
        if feedback_saved:
          messages.success(request, "Feedback Saved.")

        return shortcuts.redirect('ctstem:question_response_review', assignment_id, curriculum_question_id)

      return http.HttpResponseNotAllowed(['GET', 'POST'])

    else:
      raise models.Assignment.DoesNotExist

  except models.Assignment.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assignment not found</h1>')
  except models.CurriculumQuestion.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Question not found </h1>')

@login_required
def create_feedback_hierarchy(request, instance):
  feedback, created = models.AssignmentFeedback.objects.get_or_create(instance=instance)
  curriculum_id = instance.assignment.curriculum.id
  question_responses = models.QuestionResponse.objects.all().filter(step_response__instance=instance)

  for question_response in question_responses:
    step_feedback, created = models.StepFeedback.objects.get_or_create(assignment_feedback=feedback, step_response=question_response.step_response)
    question_feedback, created = models.QuestionFeedback.objects.get_or_create(step_feedback=step_feedback, response=question_response)

  return feedback

####################################
# Unlock submitted assignment
####################################
@login_required
def unlockAssignment(request, assignment_id='', instance_id=''):
  try:
    if '' != instance_id:
      instance = models.AssignmentInstance.objects.get(assignment__id=assignment_id, id=instance_id)
      school = instance.student.school
      group = instance.assignment.group
      has_permission = False
      #only allow Lessons to be unlocked
      if instance.assignment.curriculum.curriculum_type == 'L':
        has_permission = check_assignment_permission(request, assignment_id)

      if has_permission == False:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to unlock this assignment</h1>')

      if instance.status == 'S':
        instance.status = 'P'
        instance.last_step = instance.last_step - 1
        instance.save()
        messages.success(request, 'The assignment %s for %s has been unlocked' % (instance.assignment.curriculum, instance.student))
      else:
        messages.error(request, 'The assignment status is %s and cannot be unlocked' % (instance.status))
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
      raise models.AssignmentInstance.DoesNotExist
  except models.AssignmentInstance.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assignment not found</h1>')

####################################
# Set lock_on_completion flag for the assignment
####################################
@login_required
def lock_on_completion(request, assignment_id='', flag='0'):
  # check if the user has permission to do this operation
  has_permission = check_assignment_permission(request, assignment_id)
  response_data = {'success': False }
  if has_permission:
    assignment = models.Assignment.objects.get(id=assignment_id)
    if flag == '0':
      assignment.lock_on_completion = False
    else:
      assignment.lock_on_completion = True
    assignment.save()
    response_data['success'] = True
  return http.HttpResponse(json.dumps(response_data), content_type="application/json")

####################################
# Delete Assignment
####################################
@login_required
def deleteAssignment(request, assignment_id=''):
  # check if the user has permission to do this operation
  has_permission = check_assignment_permission(request, assignment_id)
  response_data = {'success': False }

  if has_permission:
    assignment = models.Assignment.objects.get(id=assignment_id)
    assignment_instances = models.AssignmentInstance.objects.all().filter(assignment__id=assignment_id)
    status = 'N'
    for instance in assignment_instances:
      if instance.status != 'N':
        status = instance.status
        break
    if status == 'N':
      assignment.delete()
      response_data['success'] = True

  if request.is_ajax():
    return http.HttpResponse(json.dumps(response_data), content_type="application/json")
  else:
    if has_permission:
      if status == 'N':
        messages.success(request, 'The assignment %s has been deleted' % (assignment.curriculum))
      else:
        messages.error(request, 'The assignment %s is in progress and cannot be deleted' % (assignment.curriculum))
    else:
      messages.error(request, 'You do not have the permission to delete this assignment')

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))


####################################
# Add Assignment to Group
####################################
@login_required
def addAssignment(request, curriculum_id='', group_id=''):
  # check if the user has permission to do this operation
  has_permission = check_group_permission(request, group_id)
  response_data = {'success': False }
  if has_permission:
    curriculum = models.Curriculum.objects.get(id=curriculum_id)
    group = models.UserGroup.objects.get(id=group_id)
    lock_on_completion = False
    if curriculum.curriculum_type == 'U':
      curricula = underlyingCurriculum(request, 'assign', curriculum.id)
    else:
      if curriculum.curriculum_type == 'A':
        lock_on_completion = True
      curricula = models.Curriculum.objects.all().filter(id=curriculum_id)

    for curr in curricula:
      assignment, created = models.Assignment.objects.get_or_create(group=group, curriculum=curr)
      if created and lock_on_completion:
        assignment.lock_on_completion = lock_on_completion
        assignment.save()

    response_data['success'] = True
  return http.HttpResponse(json.dumps(response_data), content_type="application/json")

####################################
# Check if the user has the permission
# to perform the specified action on the
# curriculum
####################################
def check_curriculum_permission(request, curriculum_id, action):
  try:
    has_permission = False
    is_admin = is_researcher = is_author = is_school_admin = is_teacher = False

    if hasattr(request.user, 'administrator'):
      is_admin = True
    elif hasattr(request.user, 'researcher'):
      is_researcher = True
    elif hasattr(request.user, 'author'):
      is_author = True
    elif hasattr(request.user, 'school_administrator'):
      is_school_admin = True
    elif hasattr(request.user, 'teacher'):
      is_teacher = True

    ############ CREATE ############
    if action == 'create':
      # only admin, researcher and author can create a new curriculum
      if is_admin or is_researcher or is_author or is_teacher:
        has_permission = True
      else:
        has_permission = False
        messages.error(request, 'You do not have the privilege to create a new curriculum')
    else:
      curriculum = models.Curriculum.objects.get(id=curriculum_id)
      #collaborator privileges
      has_edit_privilege = has_view_privilege = False
      if is_admin or is_researcher or is_author or is_school_admin or is_teacher:
        if curriculum.unit:
          curr = curriculum.unit
        else:
          curr = curriculum

        has_edit_privilege = models.CurriculumCollaborator.objects.all().filter(curriculum=curr, user=request.user, privilege='E').count()
        has_view_privilege = models.CurriculumCollaborator.objects.all().filter(curriculum=curr, user=request.user, privilege='V').count()

      if curriculum.status == 'R':
        if is_admin:
          if action == 'restore' or action =='preview':
            has_permission = True
      else:
        ############ COPY ############
        if action == 'copy':
          # admin, author can copy any curriculum
          if is_admin or is_author:
            has_permission = True
          # teacher and researcher can only copy units, stand alone lessons, assessments that are public or something that they own
          elif is_teacher or is_researcher:
            if curriculum.status == 'P' and curriculum.unit is None:
              has_permission = True
            elif has_view_privilege and curriculum.unit is None:
              has_permission = True
            elif has_edit_privilege:
              has_permission = True
            else:
              has_permission = False
              messages.error(request, 'You do not have the privilege to copy this curriculum')

        ############ EDIT/DELETE ############
        elif action == 'modify' or action == 'delete':
          #check if the curriculum is archived
          if curriculum.status == 'A':
            if is_admin or is_author:
              has_permission = True
            elif is_teacher or is_researcher:
              if has_edit_privilege:
                has_permission = True
            else:
              has_permission = False
              messages.error(request, 'You do not have the privilege to %s this curriculum because it is archived' % (action))
          else:
            # admin and author can edit any other curriculum
            if is_admin or is_author:
              has_permission = True
            # teacher and researcher can only edit curriculum with edit privilege
            elif is_teacher or is_researcher:
              if has_edit_privilege:
                has_permission = True
              else:
                has_permission = False
                messages.error(request, 'You do not have the privilege to %s this curriculum'% (action))

          # has permission so far
          if has_permission:
            #check if the curriculum is assigned
            is_assigned = False
            if curriculum.curriculum_type == 'U':
              for lesson in curriculum.underlying_curriculum.all():
                is_assigned = is_curriculum_assigned(request, lesson.id)
                if is_assigned:
                  break
            else:
              is_assigned = is_curriculum_assigned(request, curriculum_id)

            if is_assigned:
              if action == 'modify':
                #admins can edit any curriculum that are assigned
                # researchers and teachers can edit their curriculum that are assigned
                if is_admin or is_researcher or is_teacher:
                  has_permission = True
                  messages.warning(request, 'This curriculum has already been assigned, please be careful with the modification')
                else:
                  has_permission = False
                  messages.error(request, 'You do not have the privilege to modify this curriculum because it is already assigned')

              elif action == 'delete':
                has_permission = False
                messages.error(request, 'You do not have the privilege to delete this curriculum because it is already assigned')

        ############ PREVIEW ############
        elif action == 'preview':
          #allow everyone to preview public curricula
          if curriculum.status == 'P':
            has_permission = True
          # admin, author can preview any curricula
          elif is_admin or is_author:
            has_permission = True
          # teacher can only preview curriculum that are public, shared with them or that they own
          elif is_teacher or is_researcher:
            if has_edit_privilege or has_view_privilege:
              has_permission = True
            elif curriculum.curriculum_type == 'U':
              for lesson in curriculum.underlying_curriculum.all():
                has_permission = check_curriculum_permission(request, lesson.id, action)
                if has_permission:
                  break

          if not has_permission:
            messages.error(request, 'You do not have the privilege to preview this curriculum')

        ############ ASSIGN ############
        elif action == 'assign':
          if curriculum.curriculum_type != 'U':
            # if a non-unit curriculum is published, allow admin, school_admin and teacher to assign
            if curriculum.status == 'P':
              if is_admin or is_school_admin or is_teacher:
                has_permission = True
            #if a non-unit curriculum is private, allow all admins, and researchers/teachers who have edit/view privilege to assign the curriculum
            elif curriculum.status == 'D':
              if is_admin:
                has_permission = True
              elif is_teacher:
                if has_edit_privilege or has_view_privilege:
                  has_permission = True
          else:
            #allow a unit to be assigned only if at least one of the underlying lessons can be assigned by the user
            for lesson in curriculum.underlying_curriculum.all():
              has_permission = check_curriculum_permission(request, lesson.id, action)
              if has_permission:
                break

        ############ EXPORT RESPONSE ############
        elif action == 'export_response':
          # admin, school_admin and teacher can export student data of public curriculum
          if curriculum.status == 'P' or curriculum.status == 'A':
            if is_admin or is_researcher or is_school_admin or is_teacher:
              has_permission = True
          #only teachers and researchers can export student data of private curriculum that they own
          elif curriculum.status == 'D':
            if is_researcher or is_teacher:
              if has_edit_privilege:
                has_permission = True

          if not has_permission:
            messages.error(request, 'You do not have the privilege to export student data of this curriculum')

        ############ FAVORITE ############
        elif action == 'favorite':
          # a teacher can mark a curriculum as favorite
          if is_teacher and curriculum.unit is None:
            has_permission = True

          if not has_permission:
            messages.error(request, 'You do not have the privilege to mark this curriculum as favorite')

    return has_permission

  except models.Curriculum.DoesNotExist:
    return False

####################################
# check if the user has permission to do this operation on a group
####################################
@login_required
def check_group_permission(request, group_id=''):
  has_permission = False
  try:
    group = models.UserGroup.objects.get(id=group_id)
    if hasattr(request.user, 'administrator') == True:
      has_permission = True
    elif hasattr(request.user, 'school_administrator') and group.teacher.school == request.user.school_administrator.school:
      has_permission = True
    elif hasattr(request.user, 'teacher'):
      if group.teacher == request.user.teacher or request.user.teacher in group.shared_with.all():
        has_permission = True

  except models.UserGroup.DoesNotExist:
    has_permission = False

  return has_permission


####################################
# check if the user has permission to do this operation on assignment
####################################
@login_required
def check_assignment_permission(request, assignment_id=''):
  has_permission = False
  try:
    assignment = models.Assignment.objects.get(id=assignment_id)
    group = assignment.group
    has_permission = check_group_permission(request, group.id)

  except models.Assignment.DoesNotExist:
    has_permission = False

  return has_permission


####################################
# Export Student Responses
####################################
@login_required
def export_response(request, assignment_id='', student_id=''):
  try:
    assignment = models.Assignment.objects.get(id=assignment_id)
    group = assignment.group
    if hasattr(request.user, 'researcher'):
      has_permission = True
      if '' != student_id:
        student = models.Student.objects.get(id=student_id)
        if student.consent != 'A':
          has_permission = False
    else:
      has_permission = check_group_permission(request, group.id)

    if not has_permission:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to export student response for this assignment</h1>')

    response = http.HttpResponse(content_type='application/ms-excel')
    if '' != student_id:
      student = models.Student.objects.get(id=student_id)
      instances = models.AssignmentInstance.objects.all().filter(assignment=assignment, student=student)
      response['Content-Disposition'] = 'attachment; filename="%s-%s.xls"'% (assignment, student.user.id)
    else:
      instances = models.AssignmentInstance.objects.all().filter(assignment=assignment)
      #for researchers filter out students who have opted out
      if hasattr(request.user, 'researcher'):
        instances = instances.filter(student__consent='A')
      response['Content-Disposition'] = 'attachment; filename="%s.xls"'%assignment


    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Responses')

    row_num = 0
    bold_font_style = xlwt.XFStyle()
    bold_font_style.font.bold = True
    font_style = xlwt.XFStyle()
    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'mm/dd/yyyy'
    date_time_format = xlwt.XFStyle()
    date_time_format.num_format_str = 'mm/dd/yyyy hh:mm AM/PM'

    if hasattr(request.user, 'administrator') == True or hasattr(request.user, 'researcher') == True:
      ws.write(row_num, 0, 'School', bold_font_style)
      ws.write(row_num, 1, assignment.group.teacher.school.name, font_style)
      row_num += 1

    if hasattr(request.user, 'administrator') == True or hasattr(request.user, 'researcher') == True or hasattr(request.user, 'school_administrator') == True:
      ws.write(row_num, 0, 'Teacher', bold_font_style)
      ws.write(row_num, 1, assignment.group.teacher.user.get_full_name(), font_style)
      row_num += 1

    ws.write(row_num, 0, 'Class', bold_font_style)
    ws.write(row_num, 1, assignment.group.title, font_style)
    row_num += 1
    ws.write(row_num, 0, 'Assignment', bold_font_style)
    ws.write(row_num, 1, assignment.curriculum.title, font_style)
    row_num += 1
    ws.write(row_num, 0, 'Assigned Date', bold_font_style)
    ws.write(row_num, 1, assignment.assigned_date.replace(tzinfo=None), date_format)
    row_num += 1
    ws.write(row_num, 0, '')

    columns = ['Student', 'Student ID', 'Step No.', 'Step Title', 'Question No.', 'Question', 'Research Category', 'Options', 'Correct Answer', 'Student Response', 'Submission DateTime']
    font_styles = [font_style, font_style, font_style, font_style, font_style, font_style, font_style, font_style, font_style, font_style, date_time_format]

    row_num += 1
    for col_num in range(len(columns)):
      ws.write(row_num, col_num, columns[col_num], bold_font_style)

    for instance in instances:
      if hasattr(request.user, 'researcher'):
        student = instance.student.user.id
      else:
        student = instance.student.user.get_full_name()

      studentID = instance.student.user.id

      stepResponses = models.AssignmentStepResponse.objects.all().filter(instance=instance)
      for stepResponse in stepResponses:
        questionResponses = models.QuestionResponse.objects.all().filter(step_response=stepResponse)
        for questionResponse in questionResponses:
          response_text = get_response_text(request, instance.id, questionResponse)
          row = [student,
                 studentID,
                 stepResponse.step.order,
                 stepResponse.step.title,
                 questionResponse.curriculum_question.order,
                 smart_str(questionResponse.curriculum_question.question),
                 smart_str(",".join(str(research_category.category) for research_category in questionResponse.curriculum_question.question.research_category.all())) if questionResponse.curriculum_question.question.research_category.exists() else '',
                 smart_str(questionResponse.curriculum_question.question.options),
                 smart_str(questionResponse.curriculum_question.question.answer),
                 response_text,
                 questionResponse.modified_date.replace(tzinfo=None)]
          row_num += 1
          for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_styles[col_num])

    wb.save(response)
    return response

  except models.Assignment.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assignment not found</h1>')
  except models.Student.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested student not found</h1>')


####################################
# Export Student Responses
####################################
@login_required
def export_all_response(request, curriculum_id=''):
  # check if the user has permission to add a question
  try:
    curriculum = models.Curriculum.objects.get(id=curriculum_id)
    response = http.HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s.xls"'%curriculum.title
    wb = xlwt.Workbook(encoding='utf-8')
    bold_font_style = xlwt.XFStyle()
    bold_font_style.font.bold = True
    font_style = xlwt.XFStyle()
    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'mm/dd/yyyy'
    date_time_format = xlwt.XFStyle()
    date_time_format.num_format_str = 'mm/dd/yyyy hh:mm AM/PM'


    columns = ['Class', 'Curriculum', 'Assigned Date', 'Student', 'Student ID', 'Step No.', 'Step Title', 'Question No.', 'Question', 'Research Category', 'Options', 'Correct Answer', 'Student Response', 'Submission DateTime']
    font_styles = [font_style, font_style, date_format, font_style, font_style, font_style, font_style, font_style, font_style, font_style, font_style, font_style, font_style, date_time_format]

    if hasattr(request.user, 'administrator') == True or hasattr(request.user, 'researcher') == True or hasattr(request.user, 'school_administrator') == True:
      columns.insert(0, 'Teacher')
      font_styles.insert(0, font_style)

      if hasattr(request.user, 'administrator') == True or hasattr(request.user, 'researcher') == True:
        columns.insert(0, 'School')
        font_styles.insert(0, font_style)

    curricula = []

    if curriculum.curriculum_type != 'U':
      curricula.append(curriculum)
    else:
      curricula = curriculum.underlying_curriculum.all().order_by('order')

    for curr in curricula:
      if hasattr(request.user, 'administrator') == True or hasattr(request.user, 'researcher') == True:
        assignments = models.Assignment.objects.all().filter(curriculum__id = curr.id)
      elif hasattr(request.user, 'school_administrator') == True:
        assignments = models.Assignment.objects.all().filter(curriculum__id = curr.id, group__teacher__school = request.user.school_administrator.school)
      elif hasattr(request.user, 'teacher') == True:
        assignments = models.Assignment.objects.all().filter(Q(curriculum__id = curr.id), Q(group__teacher = request.user.teacher) | Q(group__shared_with = request.user.teacher))
      else:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to export student response for the selected curriculum</h1>')

      instances = models.AssignmentInstance.objects.all().filter(assignment__in=assignments)
      #for researchers filter out students who have opted out
      if hasattr(request.user, 'researcher'):
        instances = instances.filter(student__consent='A')

      sheet_title = curr.title
      for ch in "[]:*?/\\":
        if ch in curr.title:
          sheet_title = sheet_title.replace(ch, "-")

      #truncate sheet_title to 25 characters
      index = 1
      if curr.order:
        index = curr.order
      sheet_title = (sheet_title[:25]+' ('+str(index)+')') if len(sheet_title) > 25 else sheet_title+' ('+str(index)+')'

      ws = wb.add_sheet(sheet_title)
      row_num = 0
      #write the headers
      for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], bold_font_style)

      if instances:
        for instance in instances:
          if hasattr(request.user, 'researcher'):
            student = instance.student.user.id
          else:
            student = instance.student.user.get_full_name()

          studentID = instance.student.user.id
          stepResponses = models.AssignmentStepResponse.objects.all().filter(instance=instance)
          for stepResponse in stepResponses:
            questionResponses = models.QuestionResponse.objects.all().filter(step_response=stepResponse)
            for questionResponse in questionResponses:
              response_text = get_response_text(request, instance.id, questionResponse)
              row = [instance.assignment.group.title,
                     instance.assignment.curriculum.title,
                     instance.assignment.assigned_date.replace(tzinfo=None),
                     student,
                     studentID,
                     stepResponse.step.order,
                     stepResponse.step.title,
                     questionResponse.curriculum_question.order,
                     smart_str(questionResponse.curriculum_question.question),
                     smart_str(",".join(str(research_category.category) for research_category in questionResponse.curriculum_question.question.research_category.all())) if questionResponse.curriculum_question.question.research_category.exists() else '',
                     smart_str(questionResponse.curriculum_question.question.options),
                     smart_str(questionResponse.curriculum_question.question.answer),
                     response_text,
                     questionResponse.modified_date.replace(tzinfo=None)]
              if hasattr(request.user, 'administrator') == True or hasattr(request.user, 'researcher') == True or hasattr(request.user, 'school_administrator') == True:
                row.insert(0, instance.assignment.group.teacher.user.get_full_name())

                if hasattr(request.user, 'administrator') == True or hasattr(request.user, 'researcher') == True:
                  row.insert(0, instance.assignment.group.teacher.school.name)

              row_num += 1
              for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_styles[col_num])
      else:
        row_num += 1
        ws.write(row_num, 0, 'There are no student response for this assignment', font_style)

    wb.save(response)
    return response

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested curriculum not found</h1>')

####################################
# Get question response
# If the question type is Text return the text response
# If the question type is Sketch or Data Table return the url that will display the Sketch or Data Table
# If the question type is File, return the url(s) of the user uploaded files
####################################
@login_required
def get_response_text(request, instance_id, questionResponse):
  response_text = ''
  answer_field_type = questionResponse.curriculum_question.question.answer_field_type
  if answer_field_type == 'SK' or answer_field_type == 'DT':
    current_site = Site.objects.get_current()
    domain = current_site.domain
    response_text = 'https://%s/response/%d/%d'%(domain, instance_id, questionResponse.id)
  elif answer_field_type == 'FI':
    uploaded_files = questionResponse.response_file.all()
    response_text = ''
    for uploaded_file in uploaded_files:
      response_text = response_text + uploaded_file.file.url + '\n'
  else:
    if questionResponse.response:
      response_text = smart_str(questionResponse.response)

  return response_text

####################################
# ADD/EDIT QUESTION
####################################
@login_required
def question(request, id=''):
  # check if the user has permission to add a question
  if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False and hasattr(request.user, 'author') == False and hasattr(request.user, 'teacher') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to add a question</h1>')
  disable_fields = False
  if '' == id:
    question = models.Question()
    title = 'Add Question'
  else:
    question = models.Question.objects.get(id=id)
    curricula = models.Curriculum.objects.all().filter(steps__curriculumquestion__question=question)
    is_assigned = False
    for curriculum in curricula:
      is_assigned = is_curriculum_assigned(request, curriculum.id)
      if is_assigned:
        break
    if hasattr(request.user, 'administrator') == False and is_assigned:
      disable_fields = True
    title = 'Edit Question'

  if 'GET' == request.method:
    questionForm = forms.QuestionForm(instance=question, disable_fields=disable_fields)
    context = {'questionForm': questionForm, 'title': title, 'disable_fields': disable_fields}
    return render(request, 'ctstem_app/Question.html', context)

  elif 'POST' == request.method:
    data = request.POST.copy()
    questionForm = forms.QuestionForm(data, request.FILES, instance=question, disable_fields=disable_fields)
    response_data = {}
    if questionForm.is_valid():
      question = questionForm.save()
      response_data = {'success': True, 'question_id': question.id, 'question_text': replace_iframe_tag(request, question.question_text)}
    else:
      print(questionForm.errors)
      context = {'questionForm': questionForm, 'title': title, 'disable_fields': disable_fields}
      html = render_to_string('ctstem_app/Question.html', context, request)
      response_data = {'success': False, 'html': html, 'error': 'The question could not be saved because there were errors. Please check the errors below.'}

    return http.HttpResponse(json.dumps(response_data), content_type="application/json")

  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# Display the question response based on the answer field type
####################################
def questionResponse(request, instance_id='', response_id=''):
  try:
    if request.user.is_anonymous:
      messages.info(request, 'Please login to view the link')
      return shortcuts.redirect('ctstem:home')
    # check if the user has permission to view student response
    if '' != instance_id and '' != response_id:
      instance = models.AssignmentInstance.objects.get(id=instance_id)
      print('instance', instance)
      school = instance.student.school
      group = instance.assignment.group
      privilege = 0
      if hasattr(request.user, 'researcher') or hasattr(request.user, 'administrator'):
        privilege = 1
      elif hasattr(request.user, 'teacher') and request.user.teacher == group.teacher:
          privilege = 1
      elif hasattr(request.user, 'school_administrator') and request.user.school_administrator.school == school:
        privilege = 1

      if privilege == 0:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to view this page</h1>')

      if 'GET' == request.method:
        #get the question response
        question_response = models.QuestionResponse.objects.get(id=response_id, step_response__instance__id=instance_id)
        print('response', question_response)
        question = question_response.curriculum_question.question
        question_response_files = question_response.response_file.all()
        context = {'question': question, 'question_response': question_response, 'response_files': question_response_files}
        return render(request, 'ctstem_app/QuestionResponse.html', context)

      return http.HttpResponseNotAllowed(['GET'])
    else:
      return http.HttpResponseNotFound('<h1>Requested response not found</h1>')
  except models.AssignmentInstance.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested response not found</h1>')
  except models.QuestionResponse.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested response not found</h1>')

####################################
# GENERATE UNIQUE USER CODE
####################################
def generate_code(request):
  code = models.generate_code_helper()
  response_data = {'code': code}
  return http.HttpResponse(json.dumps(response_data), content_type="application/json")

####################################
# UPLOAD USERS
####################################
@login_required
def user_upload(request):
  if hasattr(request.user, 'administrator'):
    role = 'admin'
  elif hasattr(request.user, 'school_administrator'):
    role = 'school_administrator'
  elif hasattr(request.user, 'teacher'):
    role = 'teacher'
  else:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to upload users</h1>')

  count = 0
  added = 0
  new = 0
  invalid = 0
  added_students = {}
  msg = {'error': [], 'success': []}

  if request.method == 'POST':
    form = forms.UploadFileForm(request.POST, request.FILES, user=request.user)
    data = request.POST.copy()

    if form.is_valid():
      group = models.UserGroup.objects.get(id=data['group'])
      #read the emails in the text field
      emails = []
      if data['emails']:
        emails = [e.strip() for e in data['emails'].splitlines()]
      #read the emails in the csv and append to the previous list
      if request.FILES:
        f = request.FILES['uploadFile']
        decoded_file = f.read().decode("utf-8-sig")
        io_string = StringIO.StringIO(decoded_file)
        reader = csv.reader(io_string, delimiter=',')
        for row in reader:
          csv_email = str(row[0]).strip()
          if csv_email is not None and csv_email != '':
            emails.append(csv_email)

      for email in emails:
        count += 1
        #check email format
        try:
          validate_email(email)
          valid_email = True
        except ValidationError:
          valid_email = False

        if not valid_email:
          msg['error'].append('%s is an invalid email' % email)
          messages.error(request, '%s is an invalid email' % email)
          invalid +=1
        else:
          #check if email exists
          user_count = User.objects.filter(email=email).count()
          if user_count == 1:
            #check if email belongs to a student
            if models.Student.objects.filter(user__email=email).exists():
              student = models.Student.objects.get(user__email=email)
              #if student belongs to the same school as the teacher
              if group.teacher.school == student.school:
                membership, created = models.Membership.objects.get_or_create(student=student, group=group)
                student_consent = 'Unknown'
                if student.consent == 'A':
                  student_consent = 'Agree'
                elif student.consent == 'D':
                  student_consent = 'Disagree'
                added_students[student.id] = {'user_id': student.user.id, 'username': student.user.username,
                                              'full_name': student.user.get_full_name(), 'email': student.user.email,
                                              'status': 'Active' if student.user.is_active else 'Inactive',
                                              'student_consent':  student_consent,
                                              'member_since': student.user.date_joined.strftime('%b %d, %Y'),
                                              'last_login': student.user.last_login.strftime('%b %d, %Y') if student.user.last_login else '', 'group': group.id}
                send_added_to_group_confirmation_email(email, group)
                added += 1
              else:
                #error out email does not belong to the same school
                msg['error'].append('Email %d belongs to a student in a different school' % count)
                messages.error(request, 'Email %d belongs to a student in a different school' % count)
                invalid += 1
            else:
              #error out email in use does not belong to a student account
              msg['error'].append('Email %d does not belong to a student account' % count)
              messages.error(request, 'Email %d does not belong to a student account' % count)
              invalid += 1
          elif user_count > 1:
            #error out email because there is more than one account with that email
            msg['error'].append('Email %d used in more than one user account' % count)
            messages.error(request, 'Email %d used in more than one user account' % count)
            invalid += 1
          else:
            #email does not exist.  Send and email with registration link
            send_student_account_request_email(email, group)

            new += 1

      if added:
        msg['success'].append('Existing students added to the class: %d' % (added))
        messages.success(request, 'Existing students added to the class: %d' % (added))
      if new:
        msg['success'].append('Email sent to new students to create an account: %d' % (new))
        messages.success(request, 'Email sent to new students to create an account: %d' % (new))
      if invalid:
        msg['error'].append('Invalid emails found: %d' % (invalid))
        messages.error(request, 'Invalid emails found: %d' % (invalid))

      response_data = {'success': True, 'new_students': added_students, 'messages': msg}
    else:
      print(form.errors)
      response_data = {'success': False, 'message': 'Please select a class and either a list of student emails or a student email csv to upload.'}

    return http.HttpResponse(json.dumps(response_data), content_type="application/json")

  return http.HttpResponseNotAllowed(['POST'])

################################################
# Send account pending email to anonymous user after
# registering admin, researcher, author, school administrator account
################################################
def send_account_pending_email(role, user):
  current_site = Site.objects.get_current()
  domain = current_site.domain
  #send an email to registering user about pending account
  body = '<div> Welcome to Computational Thinking in STEM website https://%s.  <div> \
          <div> Your <b>%s</b> account is pending admin approval, and you will be notified once approved. </div>  <br>\
          <div><b>CT-STEM Admin</b></div>' % (domain, role.title())
  send_mail('CT-STEM - %s Account Pending' % role.title(), body, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=body)

  #send an email to the site admin
  body = '<div>%s has requested <b>%s</b> account on https://%s.  You may approve the user account here https://%s/user/%d/.  </div>  <br>\
          <div><b>CT-STEM Admin</b></div>' % (user.get_full_name(), role.title(), user.username, domain, domain, user.id)
  send_mail('CT-STEM - %s Account Approval Request' % role.title(), body, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL], html_message=body)

################################################
# Send account request email after
# teacher adds a new email to group
################################################
def send_student_account_request_email(email, group):
  #email user the  user name and password
  current_site = Site.objects.get_current()
  domain = current_site.domain
  body = '<div>Your teacher has requested you to create an account on Computational Thinking in STEM website </div><br> \
          <div>Click the link below and follow the instructions on the webpage to create a student account. </div><br> \
          <div>https://%s?next=/register/group/%s/%s/  </div><br> \
          <div>If clicking the link does not seem to work, you can copy and paste the link into your browser&#39;s address window, </div> \
          <div>or retype it there. Once you have returned to CT-STEM, we will give instructions for creating an account. </div><br> \
          <div><b>CT-STEM Admin</b></div>'%(domain, group.group_code, email)

  send_mail('CT-STEM - Student Account Signup Request', body, settings.DEFAULT_FROM_EMAIL, [email], html_message=body)

################################################
# Send account confirmation email after
# an admin creates an account for a subordinate
################################################
def send_account_by_admin_confirmation_email(role, user, password):
  #email user the  user name and password
  current_site = Site.objects.get_current()
  domain = current_site.domain
  body = '<div>Your <b>%s</b> account has been created on Computational Thinking in STEM website https://%s.  </div> \
          <div>Please login to the site using the credentials below and change your password immediately.  </div><br> \
          <div><b>Username:</b> %s </div> \
          <div><b>Temporary Password:</b> %s </div><br>\
          <div><b>CT-STEM Admin</b></div>'%(role.title(), domain, user.username, password)

  send_mail('CT-STEM - %s Account Created'%role.title(), body, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=body)

def send_student_account_by_self_confirmation_email(user, group):
  current_site = Site.objects.get_current()
  domain = current_site.domain
  body = '<div>Welcome to Computational Thinking in STEM website https://%s.  <div> \
          <div>You have successfully created a student account on our site.  You have also been added to the class <b>%s</b>. </div> \
          <div>Now you can login to complete your assignments. <div> <br>\
          <div>If you have forgotten your password since you last logged in, you can reset your password here https://%s/?next=/password_reset/recover/  </div><br> \
          <div><b>CT-STEM Admin</b></div>' % (domain, group.title.title(), domain)

  send_mail('CT-STEM - Student Account Created', body, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=body)

################################################
# Send an email to an existing student after
# teacher adds the student to a group
################################################
def send_added_to_group_confirmation_email(email, group):
  #email user the  user name and password
  current_site = Site.objects.get_current()
  domain = current_site.domain
  student = models.Student.objects.get(user__email=email)
  body = '<div>Your teacher has added you to the class <b>%s</b> on Computational Thinking in STEM website. </div><br> \
          <div>You may login with your username, <b>%s</b> and password here https://%s?next=/login/%s/ </div><br> \
          <div>If you have forgotten your password since you last logged in, you can reset your password here https://%s/?next=/password_reset/recover/  </div><br> \
          <div>If clicking the link does not seem to work, you can copy and paste the link into your browser&#39;s address window, </div> \
          <div>or retype it there. Once you have returned to CT-STEM, we will give instructions to proceed. </div><br> \
          <div><b>CT-STEM Admin</b></div>'%(group.title.title(), student.user.username, domain, student.user.username, domain)
  subject = 'CT-STEM - Student Account added to %s' % group.title.title()

  send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email], html_message=body)

################################################
# Send email to student when feedback is ready
# on their assignment
################################################
def send_feedback_ready_email(email, curriculum):
  current_site = Site.objects.get_current()
  domain = current_site.domain
  body = '<div>Your teacher has provided feedback on the assignment %s. </div><br> \
          <div>Please login to our website https://%s to review the feedback. </div><br> \
          <div><b>CT-STEM Admin</b></div>'%(curriculum.title, domain)

  send_mail('CT-STEM - Assignment Feedback Ready', body, settings.DEFAULT_FROM_EMAIL, [email], html_message=body)

################################################
# Send account validation email after a user
# creates a teacher account
################################################
def send_teacher_account_validation_email(teacher):
  current_site = Site.objects.get_current()
  domain = current_site.domain
  body =  '<div>Welcome to Computational Thinking in STEM. </div><br> \
           <div>Your e-mail address was used to create a teacher account on our website. If you made this request, please follow the instructions below.<div><br> \
           <div>Please click this link https://%s?next=/validate/%s/%s/ to validate your account. </div><br><br> \
           <div>If you did not request this account you can safely ignore this email. Rest assured your e-mail address and the associated account will be deleted from our system in 24 hours.</div><br> \
           <div><b>CT-STEM Admin</b></div>' % (domain, teacher.user.username, teacher.validation_code)

  send_mail('CT-STEM - Teacher Account Validation', body, settings.DEFAULT_FROM_EMAIL, [teacher.user.email], html_message=body)

################################################
# Send account approval email after
# admin approves the user account
################################################
def send_account_approval_email(user):
  current_site = Site.objects.get_current()
  domain = current_site.domain
  body = '<div>Your account has been approved on Computational Thinking in STEM website https://%s.  </div> \
          <div>Please login to the site using the the credentials created during registration. </div><br> \
          <div><b>CT-STEM Admin</b></div>'%(domain)

  send_mail('CT-STEM - Account Approved', body, settings.DEFAULT_FROM_EMAIL,[user.email], html_message=body)


################################################
# Send training request email to admin and the sender
################################################
def send_training_request_email(training):
  #send email to sender and admin
  body =  '<div>Thank you for your interest in attending our training session.  We received the following information from you.</div> <br>\
           <div><b>Name </b>: %s </div> \
           <div><b>Email </b>: %s </div> \
           <div><b>School </b>: %s </div> \
           <div><b>Subject </b>: %s </div> <br>\
           <div>We will communicate the date, place and other details about the event shortly. </div><br> \
           <div><b>CT-STEM Admin </b></div>' % (training.name, training.email, training.school, training.subject)
  send_mail('CT-STEM - Training Request', body, settings.DEFAULT_FROM_EMAIL, [training.email, settings.DEFAULT_FROM_EMAIL], html_message=body)


####################################
# Schools
####################################
@login_required
def schools(request):
  if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to view schools</h1>')

  schools = models.School.objects.all()
  context = {'schools': schools}
  return render(request, 'ctstem_app/Schools.html', context)

####################################
# Add/Edit School
####################################
@login_required
def school(request, id=''):
  try:
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to add/edit schools</h1>')

    if ''!= id:
      school = models.School.objects.get(id=id)
    else:
      school = models.School()

    if request.method == 'GET':
        form = forms.SchoolForm(instance=school, prefix='school')
        context = {'form': form,}
        return render(request, 'ctstem_app/School.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      form = forms.SchoolForm(data, instance=school, prefix="school")
      if form.is_valid():
        school = form.save()
        messages.success(request, "School Saved.")
        return shortcuts.redirect('ctstem:schools',)
      else:
        print(form.errors)
        messages.error(request, "The school could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form}
        return render(request, 'ctstem_app/School.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.School.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested publication not found</h1>')

####################################
# Delete School
####################################
def deleteSchool(request, id=''):
  try:
    # check if the user has permission to delete a school
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to delete this school</h1>')
    # check if the lesson exists
    if '' != id:
      school = models.School.objects.get(id=id)
    else:
      raise models.School.DoesNotExist

    if request.method == 'GET' or request.method == 'POST':
      print(school)
      school.delete()
      messages.success(request, '%s deleted' % school.name)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.School.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested school not found</h1>')

####################################
# Subjects
####################################
@login_required
def subjects(request):
  if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to view subjects</h1>')

  subjects = models.Subject.objects.all()
  context = {'subjects': subjects}
  return render(request, 'ctstem_app/Subjects.html', context)

####################################
# Add/Edit Subject
####################################
@login_required
def subject(request, id=''):
  try:
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to add/edit subjects</h1>')

    if ''!= id:
      subject = models.Subject.objects.get(id=id)
    else:
      subject = models.Subject()

    if request.method == 'GET':
        form = forms.SubjectForm(instance=subject, prefix='subject')
        context = {'form': form,}
        return render(request, 'ctstem_app/Subject.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()

      form = forms.SubjectForm(data, request.FILES, instance=subject, prefix="subject")
      if form.is_valid():
        form.save()
        messages.success(request, "Subject Saved.")
        return shortcuts.redirect('ctstem:subjects',)
      else:
        print(form.errors)
        messages.error(request, "The subject could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form}
        return render(request, 'ctstem_app/Subject.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Subject.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested subject not found</h1>')

####################################
# Delete Subject
####################################
def deleteSubject(request, id=''):
  try:
    # check if the user has permission to delete a subject
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to delete this subject</h1>')
    # check if the lesson exists
    if '' != id:
      subject = models.Subject.objects.get(id=id)
    else:
      raise models.Subject.DoesNotExist

    if request.method == 'GET' or request.method == 'POST':
      subject.delete()
      messages.success(request, '%s deleted' % subject.name)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Subject.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested subject not found</h1>')

####################################
# Team Roles
####################################
@login_required
def teamRoles(request):
  if hasattr(request.user, 'administrator') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to edit team roles</h1>')

  TeamRoleFormSet = modelformset_factory(models.TeamRole, form=forms.TeamRoleForm, can_delete=True, can_order=True)
  if request.method == 'GET':
    formset = TeamRoleFormSet(queryset=models.TeamRole.objects.all().order_by('order'))
    context = {'formset': formset}
    return render(request, 'ctstem_app/TeamRoles.html', context)
  elif request.method == 'POST':
    data = request.POST.copy()
    formset = TeamRoleFormSet(data, queryset=models.TeamRole.objects.all())
    if formset.is_valid():
      for form in formset.ordered_forms:
        form.instance.order = form.cleaned_data['ORDER']
        form.save()
      messages.success(request, 'Team roles saved')
      return shortcuts.redirect('ctstem:teamRoles')
    else:
      print(formset.errors)
      context = {'formset': formset}
      return render(request, 'ctstem_app/TeamRoles.html', context)
  return http.HttpResponseNotAllowed(['GET', 'POST'])


@login_required
def teamMembers(request):
  if hasattr(request.user, 'administrator') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to edit team roles</h1>')

  members = models.Team.objects.all().order_by('-current', 'order')
  context = {'members': members}
  return render(request, 'ctstem_app/TeamMembers.html', context)

@login_required
def teamMember(request, id=''):
  try:
    if hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to add/edit team members</h1>')

    if ''!= id:
      member = models.Team.objects.get(id=id)
    else:
      member = models.Team()

    if request.method == 'GET':
        form = forms.TeamMemberForm(instance=member, prefix='team')
        context = {'form': form,}
        return render(request, 'ctstem_app/TeamMember.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()

      form = forms.TeamMemberForm(data, request.FILES, instance=member, prefix="team")
      if form.is_valid():
        form.save()
        messages.success(request, "Team Member Saved.")
        return shortcuts.redirect('ctstem:teamMembers')
      else:
        print(form.errors)
        messages.error(request, "Team member could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form}
        return render(request, 'ctstem_app/TeamMember.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Subject.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested subject not found</h1>')

@login_required
def deleteMember(request, id=''):
  try:
    # check if the user has permission to delete a subject
    if hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to delete team member</h1>')
    # check if the lesson exists
    if ''!= id:
      member = models.Team.objects.get(id=id)
    else:
      raise models.Team.DoesNotExist

    if request.method == 'GET' or request.method == 'POST':
      member.delete()
      messages.success(request, '%s deleted' % member.name)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Team.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested Team Member not found</h1>')

def teamProfile(request, id=''):
  try:
    member = models.Team.objects.get(id=id)
    context = {'member': member}
    return render(request, 'ctstem_app/TeamProfile.html', context)

  except models.Team.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested member not found</h1>')

# Check session to see if it has expired
@login_required
def check_session(request):
  if 'GET' == request.method:
    data = {}
    if hasattr(request.user, 'student') == True and datetime.datetime.now() - datetime.datetime.strptime(request.session['last_touch'], "%Y-%m-%d %H:%M:%S.%f") > datetime.timedelta( 0, settings.AUTO_LOGOUT_DELAY * 60, 0):
      data['session_expired'] =  True
    else:
      data['session_expired'] =  False

    return http.HttpResponse(json.dumps(data), content_type="application/json")

  elif 'POST' == request.method:
    request.session['last_touch'] = str(datetime.datetime.now())
    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# PROFESSIONAL DEVELOPMENT PAGE
####################################
def teacherSupport(request):
  return render(request, 'ctstem_app/TeacherSupport.html')


####################################
# LIST OF PROFESSIONAL DEVELOPMENT REQUESTS
####################################
@login_required
def training_requests(request):
  if hasattr(request.user, 'administrator') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to view this page</h1>')

  if request.method == "GET" or request.method == "POST":
    trainingRequests = models.TrainingRequest.objects.all()
    context = {'trainingRequests': trainingRequests}
    return render(request, 'ctstem_app/TrainingRequests.html', context)
  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# RECORD PD REQUESTS
####################################
def request_training(request):

  training = models.TrainingRequest()
  if request.method == 'GET':
    if request.user.is_authenticated:
      initial= {'name': request.user.get_full_name(), 'email': request.user.email}
      if hasattr(request.user, 'teacher'):
        initial['school'] = request.user.teacher.school
      form = forms.TrainingRequestForm(initial=initial, instance=training)
    else:
      form = forms.TrainingRequestForm(instance=training)
    context = {'form': form}
    return render(request, 'ctstem_app/TrainingRequestModal.html', context)

  elif request.method == 'POST':
    response_data = {}
    data = request.POST.copy()

    form = forms.TrainingRequestForm(data, instance=training)
    if form.is_valid():
      #checking for bots
      if request.user.is_anonymous:
        recaptcha_response = request.POST.get('g-recaptcha-response')
        is_human = validate_recaptcha(request, recaptcha_response)
        if not is_human:
          response_data['success'] = False
          context = {'form': form, 'recaptcha_error':  'Invalid reCAPTCHA'}
          response_data['html'] = render_to_string('ctstem_app/TrainingRequestModal.html', context, request)

          return http.HttpResponse(json.dumps(response_data), content_type="application/json")

      training = form.save()
      messages.success(request, "Your request has been sent to the site admin")
      response_data['success'] = True
      #send email to the sender and admin
      send_training_request_email(training)

      return http.HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
      print(form.errors)
      response_data['success'] = False
      context = {'form': form}
      response_data['html'] = render_to_string('ctstem_app/TrainingRequestModal.html', context, request)

      return http.HttpResponse(json.dumps(response_data), content_type="application/json")

  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# Validate account
####################################
def validate(request, username='', validation_code=''):
  if request.method == 'GET':
    form = forms.ValidationForm(initial={'username': username, 'validation_code': validation_code})
    context = {'form': form}
    return render(request, 'ctstem_app/ValidationModal.html', context)
  elif request.method == 'POST':
    response_data = {}
    data = request.POST.copy()
    form = forms.ValidationForm(data)
    if form.is_valid():
      username = form.cleaned_data['username'].lower()
      password = form.cleaned_data['password']
      user = User.objects.get(username=username)
      user.is_active = True
      user.save()

      response_data['redirect_url'] = '/'
      #check if this user added a new school
      if hasattr(user, 'teacher'):
        response_data['redirect_url'] = '/groups/active/'
        school = models.School.objects.get(id=user.teacher.school.id)
        if not school.is_active:
          school.is_active = True
          school.save()

      login(request, user)
      messages.success(request, "Your account has been validated")
      response_data['success'] = True

    else:
      print(form.errors)
      context = {'form': form}
      response_data['success'] = False
      response_data['html'] = render_to_string('ctstem_app/ValidationModal.html', context, request)

    return http.HttpResponse(json.dumps(response_data), content_type="application/json")



  return http.HttpResponseNotAllowed(['GET', 'POST'])

@login_required
def subaction(request, action=1):
  if request.is_ajax():
    action = int(action)
    if 2 == action:
        data = models.School.objects.filter(~Q(school_code='OTHER'), is_active=True).order_by('name')
    else:
        return http.HttpResponse(status=400)
    data = [{'id': d['id'], 'name': d['name']} for d in data.values('id', 'name')]
    return http.HttpResponse(json.dumps(data, ensure_ascii=False), content_type='application/javascript')
  else:
    return http.HttpResponse(status=400)

@login_required
def resetPassword(request, id=''):
  if request.method in ['GET', 'POST']:
    try:
      if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'teacher') == False:
        response_data = {'result': 'Failure', 'message': 'You do not have the privilege to reset user password'}
      else:
        user = User.objects.get(id=id)
        password = User.objects.make_random_password()
        user.set_password(password)
        user.save()
        print('password reset')
        response_data = {'result': 'Success', 'full_name': user.get_full_name(), 'username': user.username, 'password': password}
      return http.HttpResponse(json.dumps(response_data), content_type="application/json")
    except models.User.DoesNotExist:
      return http.HttpResponseNotFound('<h1>Requested User not found</h1>')
  return http.HttpResponseNotAllowed(['GET', 'POST'])


# Get and Set iframe state for the
# given instance, and iframe id
@login_required
def iframe_state(request, instance_id, iframe_id):
  if request.is_ajax():
    try:
      if hasattr(request.user, 'student'):
        student = request.user.student
        instance = models.AssignmentInstance.objects.get(id=instance_id, student=student)
        if request.method == 'GET':
          iframe_url = request.GET['iframe_url']
          iframeState = models.IframeState.objects.get(instance=instance, iframe_id=iframe_id, iframe_url=iframe_url)
          response_data = {'result': 'Success', 'message': 'State retrieved', 'state': iframeState.state}
        else:
          state = request.POST['state']
          iframe_url = request.POST['iframe_url']
          obj, created = models.IframeState.objects.update_or_create(instance=instance, iframe_id=iframe_id, iframe_url=iframe_url, defaults={'state': state})
          response_data = {'result': 'Success', 'message': 'State saved'}

    except models.AssignmentInstance.DoesNotExist:
      response_data = {'result': 'Failure', 'message': 'Assignment does not exist'}
    except models.IframeState.DoesNotExist:
      response_data = {'result': 'Success', 'message': 'Iframe state does not exist', 'state': None}

    return http.HttpResponse(json.dumps(response_data), content_type="application/json")

  return http.HttpResponse(status=400)

@login_required
def is_curriculum_assigned(request, id):
  curriculum = models.Curriculum.objects.get(id=id)
  is_assigned = False

  assignment_count = models.Assignment.objects.all().filter(Q(curriculum=curriculum) | Q(curriculum__unit=curriculum)).count()
  if assignment_count > 0:
    is_assigned = True

  return is_assigned

def is_curriculum_assigned_by_me(request, id):
  curriculum = models.Curriculum.objects.get(id=id)
  is_assigned = False

  if hasattr(request.user, 'teacher'):
    assignment_count = models.Assignment.objects.all().filter(Q(curriculum=curriculum) | Q(curriculum__unit=curriculum), Q(group__teacher=request.user.teacher)).count()
    if assignment_count > 0:
      is_assigned = True

  return is_assigned

def is_curriculum_shared_with_me(request, id):
  curriculum = models.Curriculum.objects.get(id=id)
  is_shared = False
  if request.user.is_authenticated:
    view_privilege = models.CurriculumCollaborator.objects.all().filter(curriculum=curriculum, user=request.user, privilege='V').count()

    if view_privilege == 1:
      #curriculum can only be shared with teachers and researchers
      if hasattr(request.user, 'teacher') or hasattr(request.user, 'researcher'):
        is_shared = True

  return is_shared

@login_required
def is_curriculum_assigned_ajax(request, id):
  is_assigned = is_curriculum_assigned(request, id)
  response_data = {'is_assigned': is_assigned}
  return http.HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
def reorder_underlying_curricula(request, unit_id):
  curricula = models.Curriculum.objects.all().filter(unit__id=unit_id).exclude(status='R').order_by('order', '-modified_date')
  order = 1
  for curriculum in curricula:
    #fix curriculum order if it is out of order
    if curriculum.order != order:
      curriculum.order = order
      curriculum.save()
    order = order + 1

@login_required
def reorder_publications(request):
  publications = models.Publication.objects.all().order_by('order', '-modified_date')
  order = 1
  for publication in publications:
    #fix publication order if it is out of order
    if publication.order != order:
      publication.order = order
      publication.save()
    order = order + 1

def terms(request):
  context = {}
  return render(request, 'ctstem_app/TermsOfUse.html', context)

def help(request):
  context = {}
  return render(request, 'ctstem_app/HelpFAQ.html', context)

class SchoolAutocomplete(autocomplete.Select2QuerySetView):
  def get_queryset(self):
    qs = models.School.objects.all().filter(is_active=True).exclude(school_code='OTHER').order_by(Lower('name'))
    if self.q:
      qs = qs.filter(name__icontains=self.q)
    if self.request.user.is_authenticated:
      return qs
    else:
      create_school = models.School.objects.all().filter(school_code='OTHER')
      return list(create_school) + list(qs)

@login_required
def clear_cache(request):
  if hasattr(request.user, 'administrator'):
    cache.clear()
    messages.success(request, "Cache cleared.")
  return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def replace_iframe_tag(request, text):
  iframe_re = re.compile(r'<iframe.*</iframe>')
  return iframe_re.sub('<div class="iframe_replacement"><i class="far fa-file-code" title="iframe placeholder"></i></div>', text)
