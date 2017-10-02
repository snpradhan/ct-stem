from ctstem_app import models, forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django import http, shortcuts, template
from django.shortcuts import render
from django.contrib import auth, messages
from django.forms.models import inlineformset_factory, modelformset_factory
from nested_formset import nestedformset_factory
from slugify import slugify
import json
from django_xhtml2pdf.utils import render_to_pdf_response
from django.template.loader import render_to_string, get_template
from django.template import RequestContext, Context
import cStringIO as StringIO
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
import urllib2
from urllib import urlretrieve
import base64
from django.utils.encoding import smart_str, smart_unicode
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.db.models import Max, Min

####################################
# HOME
####################################
def home(request):
  #get published lessons
  if hasattr(request.user, 'student') == True:
    return shortcuts.redirect('ctstem:assignments', bucket='inbox')
  else:
    lessons = models.Curriculum.objects.all().filter(curriculum_type = 'L', status='P')[:6]
    assessments = models.Curriculum.objects.all().filter(curriculum_type = 'A', status='P')[:6]
    practices = models.Category.objects.all().filter(standard__primary=True).select_related()
    team = models.Team.objects.all().order_by('role__order', 'order')
    publications = models.Publication.objects.all()
    if request.user.is_authenticated():
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
      context = {'lessons': lessons, 'assessments' : assessments, 'practices': practices, 'team': team, 'publications': publications}
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
  team = models.Team.objects.all().order_by('order')
  context = {'team': team}
  return render(request, 'ctstem_app/Team.html', context)

####################################
# Curricula TABLE VIEW
####################################
def curricula(request, curriculum_type='', status='published', bookmark='0'):
  if curriculum_type == 'assessments':
    curr_type = ['A', 'S']
    curriculum_type = 'A'
  elif curriculum_type == 'lessons':
    curr_type = ['L']
    curriculum_type = 'L'
  elif curriculum_type == 'units':
    curr_type = ['U']
    curriculum_type = 'U'
  else:
    curr_type = ['S']
    curriculum_type = 'S'

  if status == 'draft':
    stat = 'D'
  elif status == 'archived':
    stat = 'A'
  else:
    stat = 'P'

  bookmarked = None

  if hasattr(request.user, 'administrator') or hasattr(request.user, 'researcher') or hasattr(request.user, 'author'):
    curricula = models.Curriculum.objects.all().filter(curriculum_type__in = curr_type, status = stat).order_by('title')
  elif hasattr(request.user, 'teacher'):
    if bookmark == '1':
      curricula = models.Curriculum.objects.all().filter(curriculum_type__in = curr_type, status='P', bookmarked__teacher=request.user.teacher).order_by('title')
      bookmarked = curricula
    else:
      curricula = models.Curriculum.objects.all().filter(Q(curriculum_type__in = curr_type), Q(status='P') | Q(shared_with=request.user.teacher)).order_by('title')
      bookmarked = curricula.filter(bookmarked__teacher=request.user.teacher)
    status = 'published'
  else:
    curricula = models.Curriculum.objects.all().filter(curriculum_type__in = curr_type, status='P').order_by('title')
    status = 'published'

  curricula = curricula.filter(unit__isnull=True)
  context = {'curricula': curricula, 'curriculum_type': curriculum_type, 'bookmark': bookmark, 'bookmarked': bookmarked, 'status': status}
  return render(request, 'ctstem_app/Curricula.html', context)


####################################
# CREATE MODIFY a curriculum
####################################
def curriculum(request, id=''):
  try:
    # check if the user has permission to create or modify a lesson
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False and hasattr(request.user, 'author') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to create/modify this curriculum</h1>')
    # check if the lesson exists
    if '' != id:
      curriculum = models.Curriculum.objects.get(id=id)
    else:
      curriculum = models.Curriculum()
      curriculum.author = request.user

    newQuestionForm = forms.QuestionForm()

    if request.method == 'GET':
      form = forms.CurriculumForm(instance=curriculum, prefix='curriculum')
      #AssessmentStepFormSet = inlineformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,can_delete=True, can_order=True, extra=1)

      StepFormSet = nestedformset_factory(models.Curriculum, models.Step, form=forms.StepForm,
                                                    nested_formset=inlineformset_factory(models.Step, models.CurriculumQuestion, form=forms.CurriculumQuestionForm, can_delete=True, can_order=True, extra=1),
                                                    can_delete=True, can_order=True, extra=1)
      AttachmentFormSet = inlineformset_factory(models.Curriculum, models.Attachment, form=forms.AttachmentForm, can_delete=True, extra=1)

      formset = StepFormSet(instance=curriculum, prefix='form')
      attachment_formset = AttachmentFormSet(instance=curriculum, prefix='attachment_form')
      context = {'form': form, 'attachment_formset': attachment_formset, 'formset':formset, 'newQuestionForm': newQuestionForm}
      return render(request, 'ctstem_app/Curriculum.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      form = forms.CurriculumForm(data, request.FILES, instance=curriculum, prefix="curriculum")
      #AssessmentStepFormSet = inlineformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,
                                                    #can_delete=True, can_order=True, extra=0)
      StepFormSet = nestedformset_factory(models.Curriculum, models.Step, form=forms.StepForm,
                                                    nested_formset=inlineformset_factory(models.Step, models.CurriculumQuestion, form=forms.CurriculumQuestionForm, can_delete=True, can_order=True, extra=1),
                                                    can_delete=True, can_order=True, extra=1)
      AttachmentFormSet = inlineformset_factory(models.Curriculum, models.Attachment, form=forms.AttachmentForm, can_delete=True, extra=1)

      formset = StepFormSet(data, instance=curriculum, prefix='form')
      attachment_formset = AttachmentFormSet(data, request.FILES, instance=curriculum, prefix='attachment_form')

      if form.is_valid() and formset.is_valid() and attachment_formset.is_valid():
        savedCurriculum = form.save(commit=False)
        if '' == id:
            savedCurriculum.author = request.user
        savedCurriculum.slug = slugify(savedCurriculum.title) + '-v%s'%savedCurriculum.version
        savedCurriculum.save()
        form.save()
        attachment_formset.save()
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

        messages.success(request, "Curriculum Saved.")
        return shortcuts.redirect('ctstem:curriculum', id=savedCurriculum.id)
      else:
        print form.errors
        print formset.errors
        print attachment_formset.errors
        messages.error(request, "The curriculum could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form, 'attachment_formset': attachment_formset, 'formset':formset, 'newQuestionForm': newQuestionForm}
        return render(request, 'ctstem_app/Curriculum.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested curriculum not found</h1>')

####################################
# PREVIEW A Curriculum
####################################
def previewCurriculum(request, id='', step_order=-1):
  try:
    # check if the lesson exists
    if hasattr(request.user, 'student'):
      return http.HttpResponseNotFound('<h1>You do not have the privilege to preview this curriculum</h1>')

    if '' != id:
      curriculum = models.Curriculum.objects.get(id=id)
    else:
      curriculum = models.Curriculum()

    #teachers are only allowed to preview published or shared curriculum
    if curriculum.status == 'D':
      if hasattr(request.user, 'teacher') and curriculum.shared_with.all().filter(id=request.user.teacher.id).exists() == False:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to preview this curriculum</h1>')
      elif hasattr(request.user, 'school_administrator'):
        return http.HttpResponseNotFound('<h1>You do not have the privilege to preview this curriculum</h1>')

    if request.method == 'GET':
      steps = models.Step.objects.all().filter(curriculum=curriculum)
      attachments = models.Attachment.objects.all().filter(curriculum=curriculum)
      systems = models.System.objects.all()
      total_steps = len(steps)

      # for assessment and survey go to the first step
      if curriculum.curriculum_type != 'U' and curriculum.curriculum_type != 'L' and step_order == -1:
        step_order = 0

      context = {'curriculum': curriculum, 'attachments': attachments, 'systems': systems, 'total_steps': total_steps, 'step_order': step_order}

      if int(step_order) > 0:
        step = steps.get(order=int(step_order))
        context['step'] = step

      context['steps'] = steps

      return render(request, 'ctstem_app/CurriculumPreview.html', context)

    return http.HttpResponseNotAllowed(['GET'])

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
  html  = render_to_string(template_src, context_dict, context_instance=RequestContext(request))
  result = StringIO.StringIO()
  pdf = pisa.pisaDocument(StringIO.StringIO(html.encode('utf-8')), dest=result, link_callback=fetch_resources, encoding='utf-8')
  if not pdf.err:
    return http.HttpResponse(result.getvalue(), content_type='application/pdf')
  return http.HttpResponse('We had some errors! %s' % escape(html))


####################################
# Download Lesson attachments
####################################
def downloadAttachments(request, id=''):
  try:
    # check if the lesson exists
    if '' != id:
      curriculum = models.Curriculum.objects.get(id=id)
    else:
      raise models.Curriculum.DoesNotExist

    if request.method == 'GET' or request.method == 'POST':
      # Files (local path) to put in the .zip
      # FIXME: Change this (get paths from DB etc)
      # check if the user has permission to delete a lesson
      if request.user.is_anonymous() or hasattr(request.user, 'student'):
        attachments = models.Attachment.objects.all().filter(curriculum=curriculum, teacher_only=False)
      else:
        attachments = models.Attachment.objects.all().filter(curriculum=curriculum)

      # Folder name in ZIP archive which contains the above files
      # E.g [thearchive.zip]/somefiles/file2.txt
      # FIXME: Set this to something better
      zip_subdir = curriculum.title
      zip_filename = "%s.zip" % zip_subdir

      # Open StringIO to grab in-memory ZIP contents
      s = StringIO.StringIO()

      # The zip compressor
      zf = zipfile.ZipFile(s, "w")

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

      # Grab ZIP file from in-memory, make response with correct MIME-type
      response = http.HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
      # ..and correct content-disposition
      response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

      return response

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested Curriculum not found</h1>')
####################################
# DELETE a curriculum
####################################
def deleteCurriculum(request, id=''):
  try:
    # check if the user has permission to delete a lesson
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False and hasattr(request.user, 'author') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to delete this curriculum</h1>')
    # check if the lesson exists
    if '' != id:
      curriculum = models.Curriculum.objects.get(id=id)
    else:
      raise models.Curriculum.DoesNotExist

    if request.method == 'GET' or request.method == 'POST':
      curriculum.delete()
      messages.success(request, 'Curriculum %s deleted' % curriculum.title)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assessment not found</h1>')

####################################
# Curriculum Copy
####################################
def copyCurriculum(request, id=''):
  try:
    # check if the user has permission to create or modify a curriculum
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False and hasattr(request.user, 'author') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to modify this curriculum</h1>')
    # check if the curriculum exists
    else:
      if request.method == 'GET' or request.method == 'POST':
        if '' != id:
          original_curriculum = models.Curriculum.objects.get(id=id)
          # non unit copy
          if original_curriculum.curriculum_type != 'U':
            new_curriculum = copyCurriculumMeta(request, id)
            copyCurriculumSteps(request, original_curriculum, new_curriculum)
          else:
            #unit copy
            #copy unit metadata
            new_unit = copyCurriculumMeta(request, id)
            #copy underlying lessons
            for lesson in original_curriculum.underlying_curriculum.all():
              new_lesson = copyCurriculumMeta(request, lesson.id)
              copyCurriculumSteps(request, lesson, new_lesson)
              new_lesson.unit = new_unit
              new_lesson.save()

          messages.success(request, "A new copy of %s created.  Please archive the original curriculum" % original_curriculum.title)
          return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))
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
    curriculum.title = str(datetime.datetime.now())
    curriculum.slug = slugify(curriculum.title)
    curriculum.pk = None
    curriculum.id = None
    curriculum.icon = None
    curriculum.save()

    original_curriculum = models.Curriculum.objects.get(id=id)
    curriculum.title = title
    curriculum.authors = original_curriculum.authors.all()
    curriculum.created_date = datetime.datetime.now()
    curriculum.modified_date = datetime.datetime.now()
    curriculum.parent = original_curriculum
    curriculum.status = 'D'
    curriculum.version = int(original_curriculum.version) + 1
    curriculum.slug = slugify(curriculum.title) + '-v%s'%curriculum.version + '-%s'%curriculum.id
    curriculum.subject = original_curriculum.subject.all()
    curriculum.taxonomy = original_curriculum.taxonomy.all()

    if original_curriculum.icon:
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
    else:
      curriculum.save()

    for attachment in attachments:
      source = attachment.file_object
      filecontent = ContentFile(source.file.read())
      filename = os.path.split(source.file.name)[-1]
      filename_array = filename.split('.')
      filename = filename_array[0] + '-' + str(curriculum.id) + '.' + filename_array[1]
      attachment.pk = None
      attachment.id = None
      attachment.curriculum = curriculum
      attachment.file_object.save(filename, filecontent)
      attachment.save()
      source.file.close()

    return curriculum
  else:
    return None

@login_required
def copyCurriculumSteps(request, original_curriculum, new_curriculum):

  steps = models.Step.objects.all().filter(curriculum=original_curriculum)

  for step in steps:
    step_questions = models.CurriculumQuestion.objects.all().filter(step=step)
    step.pk = None
    step.id = None
    step.curriculum = new_curriculum
    step.save()
    for step_question in step_questions:
      question = step_question.question
      question.id = None
      question.pk = None
      question.save()

      step_question.id = None
      step_question.pk = None
      step_question.question = question
      step_question.step = step
      step_question.save()
  return

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
# Assign curriculum
####################################
def assignCurriculum(request, id=''):
  try:
    # check if the user has permission to bookmark a curriculum
    if hasattr(request.user, 'administrator') or hasattr(request.user, 'researcher'):
      groups = models.UserGroup.objects.all()
    elif hasattr(request.user, 'school_administrator'):
      groups = models.UserGroup.objects.all().filter(teacher__school = request.user.school_administrator.school)
    elif hasattr(request.user, 'teacher'):
      groups = models.UserGroup.objects.all().filter(teacher = request.user.teacher)
    else:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to assign this curriculum</h1>')

    curriculum = models.Curriculum.objects.get(id=id)
    if curriculum.status == 'D':
      return http.HttpResponseNotFound("<h1>This curriculum hasn't been published and cannot be assigned</h1>")
    #check if curriculum is stand alone or a unit
    if curriculum.curriculum_type == 'U':
      curriculum_list = models.Curriculum.objects.all().filter(unit=curriculum, status='P')
    else:
      curriculum_list = models.Curriculum.objects.all().filter(id=curriculum.id)

    assignments = models.Assignment.objects.all().filter(curriculum__in=curriculum_list, group__in=groups)
    assignment_dates = {}
    instances = {}
    for group in groups:
      instances[group.id] = {}
      assignment_dates[group.id] = {}
      if curriculum.curriculum_type == 'U':
        dates = assignments.filter(group=group).aggregate(Min('assigned_date'), Max('due_date'))
        assignment_dates[group.id][curriculum.id] = {'assigned_date': dates['assigned_date__min'], 'due_date': dates['due_date__max']}

      for curr in curriculum_list:
        dates = assignments.filter(group=group, curriculum=curr).aggregate(Min('assigned_date'), Max('due_date'))
        assignment_dates[group.id][curr.id] = {'assigned_date': dates['assigned_date__min'], 'due_date': dates['due_date__max']}
        instances[group.id][curr.id] = models.AssignmentInstance.objects.all().filter(assignment__curriculum=curr, assignment__group=group).count()

    if request.method == 'GET':
      context = {'curriculum': curriculum, 'curriculum_list': curriculum_list, 'groups': groups, 'assignments': assignments, 'instances': instances, 'assignment_dates': assignment_dates}
      return render(request, 'ctstem_app/CurriculumAssignment.html', context)
    elif request.method == 'POST':
      data = request.POST.copy()
      #iterate over all possible (group, curriculum) assignment combinations
      for group in groups:
        for curr in curriculum_list:
          #check if an assignment already exists
          assignment = assignments.filter(group=group, curriculum=curr).first()
          assigned_date_key = 'assigned_%s_%s'%(str(group.id), str(curr.id))
          due_date_key = 'due_%s_%s'%(str(group.id), str(curr.id))
          #if assignment already exists, check if the dates have changed
          if assignment:
            if due_date_key in data and data[due_date_key]:
              due_date = data[due_date_key]
              if assigned_date_key in data and data[assigned_date_key]:
                assigned_date = data[assigned_date_key]
                assigned_date_object = datetime.datetime.strptime(assigned_date, '%B %d, %Y')
              else:
                assigned_date_object = datetime.datetime.now()
              due_date_object = datetime.datetime.strptime(due_date, '%B %d, %Y')

              # check if due date has changed and update
              if assignment.due_date.date() != due_date_object.date() or assignment.assigned_date.date() != assigned_date_object.date():
                assignment.due_date = due_date_object
                assignment.assigned_date = assigned_date_object
                assignment.save()
            else:
              #assignment has been unmarked for deletion
              assignment.delete()
          else:
            #check if new assignment has been made
            if due_date_key in data and data[due_date_key]:
              due_date = data[due_date_key]
              if assigned_date_key in data and data[assigned_date_key]:
                assigned_date = data[assigned_date_key]
                assigned_date_object = datetime.datetime.strptime(assigned_date, '%B %d, %Y')
              else:
                assigned_date_object = datetime.datetime.now()
              due_date_object = datetime.datetime.strptime(due_date, '%B %d, %Y')
              new_assignment = models.Assignment(curriculum=curr, group=group, due_date=due_date_object, assigned_date=assigned_date_object)
              new_assignment.save()

      response_data = {'message': 'The curriculum "%s" has been assigned' % curriculum.title}
      return http.HttpResponse(json.dumps(response_data), content_type="application/json")

    return http.HttpResponseNotAllowed(['GET', 'POST'])
  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested curriculum not found</h1>')

####################################
# REGISTER
####################################
def register(request, group_id=''):
  if group_id:
    group = models.UserGroup.objects.get(id=group_id)
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
    # checking for bot signup
    #Agree checkbox is visible to the user while condition checkbox is hidden.
    #The user needs to check the Agree checkbox to enable the Register button
    #Ensure the agree checkbox is checked and the condition checkbox is unchecked to verify the request is sent by a real person
    if 'condition' in request.POST:
      #this is a bot
      #do not sign them up but show a deceiving message that they are signed up and redirect them to the homepage
      messages.info(request, 'Thank you for registering')
      return shortcuts.redirect('ctstem:home')
    else:
      #print request.POST.copy()
      school_form = None
      new_school = None
      if group_id:
        form = forms.RegistrationForm(user=request.user, data=request.POST, group_id=group_id)
      else:
        form = forms.RegistrationForm(user=request.user, data=request.POST)
        if request.user.is_anonymous():
          school_form = forms.SchoolForm(data=request.POST, instance=school, prefix="school")

      if form.is_valid():
        print form.cleaned_data
        user = User.objects.create_user(form.cleaned_data['username'],
                                        form.cleaned_data['email'],
                                        form.cleaned_data['password1'])
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        #Admin, Researcher, Author, School Admin or Teacher account created by anonymous user is set as inactive
        if form.cleaned_data['account_type'] in  ['A', 'R', 'C', 'P', 'T'] and request.user.is_anonymous():
            user.is_active = False
        else:
            user.is_active = True
        user.save()

        if form.cleaned_data['account_type'] == 'T':
          newUser = models.Teacher()
          #generate validation code
          newUser.validation_code = get_random_string(length=5)

          #get the school id
          selected_school = form.cleaned_data['school']
          if selected_school.school_code == 'OTHER':
            if school_form.is_valid():
              #create a new school entry
              new_school = school_form.save(commit=False)
              new_school.save()
              newUser.school = new_school
            else:
              print school_form.errors
              user.delete()
              context = {'form': form, 'school_form': school_form, 'other_school': other_school }
              return render(request, 'ctstem_app/Registration.html', context)

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

        elif form.cleaned_data['account_type'] == 'P':
            newUser = models.SchoolAdministrator()
            newUser.user = user
            newUser.save()

        elif form.cleaned_data['account_type'] == 'A':
            newUser = models.Administrator()
            newUser.user = user
            newUser.save()

        elif form.cleaned_data['account_type'] == 'R':
          newUser = models.Researcher()
          newUser.user = user
          newUser.save()
        elif form.cleaned_data['account_type'] == 'C':
          newUser = models.Author()
          newUser.user = user
          newUser.save()


        current_site = Site.objects.get_current()
        domain = current_site.domain

        if request.user.is_anonymous():
          if form.cleaned_data['account_type'] in ['A', 'R', 'C', 'P']:
            #send an email to the registering user
            messages.info(request, 'Your account is pending admin approval.  You will be notified once your account is approved.')
            #send email confirmation
            send_mail('CT-STEM Account Pending',
            'Welcome to Computational Thinking in STEM website http://%s.  \r\n\r\n \
            Your account is pending approval, and you will be notified once approved.\r\n\r\n  \
            -- CT-STEM Admin' % domain,
                      settings.DEFAULT_FROM_EMAIL,
                      [newUser.user.email])

            #send an email to the site admin
            send_mail('CT-STEM Account Approval Request',
            'Please approve the user account for %s on http://%s.  \r\n\r\n \
            -- CT-STEM Admin' % (user.username, domain),
                      settings.DEFAULT_FROM_EMAIL,
                      [settings.DEFAULT_FROM_EMAIL])
            return shortcuts.redirect('ctstem:home')
          #teacher account
          elif form.cleaned_data['account_type'] == 'T':
            #send an email with the username and validation code to validate the account
            messages.info(request, 'An email has been sent to %s to validate your account.  Please validate your account with in 24 hours.' % newUser.user.email)
            send_account_validation_email(newUser)

            return shortcuts.redirect('ctstem:home')

          #student account
          elif form.cleaned_data['account_type'] == 'S':
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'], )
            login(request, new_user)
            messages.info(request, 'Your have successfully registered.')
            send_mail('CT-STEM Account Created',
            'Welcome to Computational Thinking in STEM website http://%s.  \r\n\r\n \
            You can login using the credentials created during registration. \r\n\r\n \
            -- CT-STEM Admin' % domain,
                      settings.DEFAULT_FROM_EMAIL,
                      [newUser.user.email])
            return shortcuts.redirect('ctstem:home')

        else:
          messages.info(request, 'User account has been created.')

          send_mail('CT-STEM Account Created',
          'Your user account has been created on Computational Thinking in STEM website http://%s.  \r\n\r\n \
           Please login to the site using the following credentials and change your password.\r\n\r\n  \
           Username: %s \r\n \
           Temporary Password: %s \r\n\r\n \
           -- CT-STEM Admin'%(domain, newUser.user.username, form.cleaned_data['password1']),
                      settings.DEFAULT_FROM_EMAIL,
                      [newUser.user.email])

          if form.cleaned_data['account_type'] == 'A':
            return shortcuts.redirect('ctstem:users', role='admins')
          elif form.cleaned_data['account_type'] == 'R':
            return shortcuts.redirect('ctstem:users', role='researchers')
          elif form.cleaned_data['account_type'] == 'P':
            return shortcuts.redirect('ctstem:users', role='school_administrators')
          elif form.cleaned_data['account_type'] == 'C':
            return shortcuts.redirect('ctstem:users', role='authors')
          elif form.cleaned_data['account_type'] == 'T':
            return shortcuts.redirect('ctstem:users', role='teachers')
          elif form.cleaned_data['account_type'] == 'S':
            return shortcuts.redirect('ctstem:users', role='students')
          return render(request, 'ctstem_app/About_us.html')

      else:
        print form.errors
        if group_id:
          context = {'form': form, 'group_id': group_id, 'school_id': school.id}
        else:
          context = {'form': form, 'school_form': school_form, 'other_school': other_school }

        return render(request, 'ctstem_app/Registration.html', context)

  else:
    print request.user

    if hasattr(request.user, 'researcher') or hasattr(request.user, 'author') or hasattr(request.user, 'student'):
      messages.error(request, 'You do not have the privilege to register any other user')
      return shortcuts.redirect('ctstem:home')

    if group_id and 'email' in request.GET:
      email = request.GET['email']
      form = forms.RegistrationForm(initial={'email': email}, user=request.user, group_id=group_id)
      context = {'form': form, 'group_id': group_id, 'school_id': school.id}
    elif request.user.is_anonymous():
      form = forms.RegistrationForm(user=request.user)
      school_form = forms.SchoolForm(instance=school, prefix='school')
      context = {'form': form, 'school_form': school_form, 'other_school': other_school}
    elif hasattr(request.user, 'school_administrator'):
      school = request.user.school_administrator.school
      print school.id
      form = forms.RegistrationForm(user=request.user)
      context = {'form': form, 'school_id': school.id}
    elif hasattr(request.user, 'teacher'):
      school = request.user.teacher.school
      form = forms.RegistrationForm(user=request.user)
      context = {'form': form, 'school_id': school.id}
    else:
      form = forms.RegistrationForm(user=request.user)
      context = {'form': form}

    return render(request, 'ctstem_app/Registration.html', context)

####################################
# USER LOGIN
####################################
def user_login(request):
  username = password = ''
  if 'POST' == request.method:
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    response_data = {}
    if user is not None and user.is_active:
      login(request, user)
      response_data['result'] = 'Success'
      if hasattr(user, 'teacher'):
        messages.success(request, "Welcome to the CT-STEM website.  If you need help with using the site, you can checkout the help videos on the Training page <a href='/training#help_videos'>here</a>", extra_tags='safe');
      else:
        messages.success(request, "You have logged in")
    else:
      response_data['result'] = 'Failed'
      if user and user.is_active == False:
        response_data['message'] = 'Your account has not been activated'
      else:
        response_data['message'] = 'Your username and/or password is invalid'
    return http.HttpResponse(json.dumps(response_data), content_type="application/json")

  elif 'GET' == request.method:
    return shortcuts.redirect('ctstem:home')

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

      context = {'profileform': profileform, 'userform': userform, 'role': role}
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

      if userform.is_valid():
        if profileform is None:
          userform.save()
          messages.success(request, "User profile saved successfully")
          context = {'userform': userform, 'role': role}
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
          context = {'profileform': profileform, 'userform': userform, 'role': role}
        else:
          print profileform.errors
          messages.error(request, "User profile could not be saved. Please check the errors below.")
          context = {'profileform': profileform, 'userform': userform, 'role': role}
      else:
        print userform.errors
        if profileform:
          print profileform.errors
        messages.error(request, "User profile could not be saved. Please check the errors below.")
        context = {'profileform': profileform, 'userform': userform, 'role': role}

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
      response_data['result'] = 'Success'
      messages.success(request, "Thank you for submitting the opt-in form")
    else:
      response_data['result'] = 'Failed'
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
    if request.user.is_anonymous():
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
  curricula = models.Curriculum.objects.all().filter(authors__in=[user])
  flag = True
  if len(curricula) > 0:
    #get an admin to transfer the curriculum ownership to
    admin = models.Administrator.objects.all().order_by('user__date_joined')[0]
    if admin:
      for curriculum in curricula:
        # if the curriculum has only one author, set the author to an admin
        if curriculum.authors.count() == 1:
          curriculum.authors.add(admin.user)
          curriculum.save()
      messages.success(request, 'Curriculum owned by %s has been trasferred to %s' % (user.username, admin.user.username))
    else:
      messages.success(request, 'No admins exists to transfer ownership of curriculum authored by %s. So the user cannot be deleted.' % user.username)
      flag = False
  return flag

def removeStudent(request, group_id='', student_id=''):
  try:
    # check if the user has permission to create or modify a group
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'school_administrator') == False and hasattr(request.user, 'teacher') == False :
      return http.HttpResponseNotFound('<h1>You do not have the privilege to remove users from this group</h1>')
    # check if the lesson exists

    group = models.UserGroup.objects.get(id=group_id)
    student = models.Student.objects.get(id=student_id)
    if hasattr(request.user, 'teacher'):
      if request.user.teacher != group.teacher:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to remove users from this group</h1>')
    elif hasattr(request.user, 'school_administrator'):
      if request.user.school_administrator.school != group.teacher.school:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to remove users from this group</h1>')

    if request.method == 'GET' or request.method == 'POST':
      membership = models.Membership.objects.get(group=group, student=student)
      membership.delete()
      response_data = {'result': 'Success'}
      return http.HttpResponse(json.dumps(response_data), content_type="application/json")

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.UserGroup.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested group not found</h1>')
  except models.Student.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested student not found</h1>')

def addStudent(request, group_id='', student_id=''):
  try:
    # check if the user has permission to create or modify a group
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'school_administrator') == False and hasattr(request.user, 'teacher') == False :
      return http.HttpResponseNotFound('<h1>You do not have the privilege to add users from this group</h1>')
    # check if the lesson exists

    group = models.UserGroup.objects.get(id=group_id)
    student = models.Student.objects.get(id=student_id)
    if hasattr(request.user, 'teacher'):
      if request.user.teacher != group.teacher:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to remove users from this group</h1>')
    elif hasattr(request.user, 'school_administrator'):
      if request.user.school_administrator.school != group.teacher.school:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to remove users from this group</h1>')

    if request.method == 'POST':
      membership = models.Membership.objects.get_or_create(group=group, student=student)
      response_data = {'result': 'Success'}
      return http.HttpResponse(json.dumps(response_data), content_type="application/json")

    return http.HttpResponseNotAllowed(['POST'])

  except models.UserGroup.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested group not found</h1>')
  except models.Student.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested student not found</h1>')

def createStudent(request, group_id=''):
  try:
    # check if the user has permission to create a student
    import re
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'school_administrator') == False and hasattr(request.user, 'teacher') == False :
      return http.HttpResponseNotFound('<h1>You do not have the privilege to create a student</h1>')
    if request.method == 'POST':
      data=request.POST
      response_data = {}
      username = data['username']
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
                          'student_consent': student.get_consent(), 'parental_consent': student.get_parental_consent(), 'member_since': user.date_joined.strftime('%B %d, %Y')}
                        }

        send_account_confirmation_email(user, password)

      return http.HttpResponse(json.dumps(response_data), content_type="application/json")
    return http.HttpResponseNotAllowed(['POST'])

  except models.UserGroup.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested group not found</h1>')
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
      print form.is_valid()
      print formset.is_valid()
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
        print form.errors
        print formset.errors
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
  if hasattr(request.user, 'author') == False and hasattr(request.user, 'researcher') == False and  hasattr(request.user, 'administrator') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege search taxonomy</h1>')

  subcategory = models.Subcategory()
  title = 'Search Standards'
  if 'GET' == request.method:
    form = forms.TaxonomySearchForm(instance=subcategory)
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
    print query_filter
    taxonomyList = models.Subcategory.objects.filter(**query_filter)
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

  if 'POST' == request.method:
    data = request.POST.copy()
    print data
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

    print query_filter
    studentList = models.Student.objects.filter(**query_filter)
    student_list = [{'user_id': student.user.id, 'student_id': student.id, 'username': student.user.username, 'name': student.user.get_full_name(),
                     'email': student.user.email, 'status': 'Active' if student.user.is_active else 'Inactive',
                     'last_login': student.user.last_login.strftime('%B %d, %Y') if student.user.last_login else '',
                     'group': group.id, 'student_consent': student.get_consent(), 'parental_consent': student.get_parental_consent(),
                     'member_since': student.user.date_joined.strftime('%B %d, %Y')}
                for student in studentList]
    return http.HttpResponse(json.dumps(student_list), content_type="application/json")

  return http.HttpResponseNotAllowed(['POST'])

####################################
# Search Teachers
####################################
@login_required
def searchTeachers(request):
  # check if the user has permission to add a question
  if hasattr(request.user, 'author') == False and hasattr(request.user, 'researcher') == False and  hasattr(request.user, 'administrator') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege search teachers</h1>')

  if 'GET' == request.method:
    teacherSearchForm = forms.TeacherSearchForm()
    context = {'teacherSearchForm': teacherSearchForm}
    return render(request, 'ctstem_app/TeacherSearch.html', context)

  elif 'POST' == request.method:
    data = request.POST.copy()
    print data
    query_filter = {}
    if data['username']:
      query_filter['user__username__icontains'] = str(data['username'])
    if data['first_name']:
      query_filter['user__first_name__icontains'] = str(data['first_name'])
    if data['last_name']:
      query_filter['user__last_name__icontains'] = str(data['last_name'])
    if data['email']:
      query_filter['user__email__icontains'] = str(data['email'])

    print query_filter
    teacherList = models.Teacher.objects.filter(**query_filter)
    print teacherList
    teacher_list = [{'user_id': teacher.user.id, 'teacher_id': teacher.id, 'username': teacher.user.username, 'name': teacher.user.get_full_name(),
                     'email': teacher.user.email}
                for teacher in teacherList]
    return http.HttpResponse(json.dumps(teacher_list), content_type="application/json")

  return http.HttpResponseNotAllowed(['GET', 'POST'])
####################################
# USER LIST
####################################
@login_required
def users(request, role):

  if request.method == 'GET' or request.method == 'POST':

    if request.method == 'POST':
      data = request.POST.copy()
      id_list = []
      for key in data:
        if 'user_' in key:
          id_list.append(data[key])
      _do_action(request, id_list, 'user')

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

    uploadForm = forms.UploadFileForm(user=request.user)
    context = {'users': users, 'role': role, 'uploadForm': uploadForm}

    return render(request, 'ctstem_app/Users.html', context)

  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# BULK ACTION FOR ALL MODELS
####################################
@login_required
def _do_action(request, id_list, model, object_id=None):
  action_params = request.POST
  if u'' == action_params.get('action') or len(id_list) == 0:
    return True
  if model == 'user' or model == 'student':
    if model == 'user':
      users = User.objects.filter(id__in=id_list)
    elif model == 'student':
      users = User.objects.filter(student__id__in=id_list)

    if u'delete_selected' == action_params.get(u'action'):
      for user in users:
        transferCurriculum(request, user)
      users.delete()
      messages.success(request, "Selected user(s) deleted.")
      return True
    if u'remove_selected' == action_params.get(u'action'):
      for user in users:
        removeStudent(request, object_id, user.student.id)
      messages.success(request, "Selected student(s) removed from group.")
      return True
    elif u'activate_selected' == action_params.get(u'action'):
      for user in users:
        user.is_active = True
        user.save()
      messages.success(request, "Selected user(s) activated.")
      return True
    elif u'inactivate_selected' == action_params.get(u'action'):
      for user in users:
        user.is_active = False
        user.save()
      messages.success(request, "Selected user(s) inactivated.")
      return True
    elif u'parental_consent_selected' == action_params.get(u'action'):
      if u'subaction' in action_params:
        consent = action_params.get(u'subaction')
        for user in users:
          student = user.student
          student.parental_consent = consent
          student.save()
        messages.success(request, "Selected students' parental consent updated.")
        return True
      else:
        return False
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
# PUBLICATIONS TABLE VIEW
####################################
def publications(request):
  publications = models.Publication.objects.all().order_by('created')
  context = {'publications': publications}
  return render(request, 'ctstem_app/Publications.html', context)

####################################
# CREATE MODIFY A PUBLICATION
####################################
@login_required
def publication(request, slug=''):
  try:
    # check if the user has permission to create or modify a lesson
    if hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to modify this publication</h1>')
    # check if the lesson exists
    if 'new' != slug:
      publication = models.Publication.objects.get(slug=slug)
    else:
      publication = models.Publication()

    if request.method == 'GET':
        form = forms.PublicationForm(instance=publication, prefix='publication')
        context = {'form': form,}
        return render(request, 'ctstem_app/Publication.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      print request.FILES
      form = forms.PublicationForm(data, request.FILES, instance=publication, prefix="publication")
      if form.is_valid():
        savedPublication = form.save(commit=False)
        savedPublication.slug = slugify(savedPublication.title)
        savedPublication.save()
        form.save()
        messages.success(request, "Publication Saved.")
        return shortcuts.redirect('ctstem:publications',)
      else:
        print form.errors
        messages.error(request, "The publication could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form}
        return render(request, 'ctstem_app/Publication.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Publication.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested publication not found</h1>')

####################################
# DELETE PUBLICATION
####################################
def deletePublication(request, slug=''):
  try:
    # check if the user has permission to delete a lesson
    if hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to delete this publication</h1>')
    # check if the lesson exists
    if '' != slug:
      publication = models.Publication.objects.get(slug=slug)
    else:
      raise models.Publication.DoesNotExist

    if request.method == 'GET' or request.method == 'POST':

      publication.delete()
      messages.success(request, '%s deleted' % publication.title)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Publication.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested publication not found</h1>')


####################################
# GROUPS TABLE VIEW
####################################
@login_required
def groups(request):
  if hasattr(request.user, 'administrator') or hasattr(request.user, 'researcher'):
    groups = models.UserGroup.objects.all().order_by('id')
  elif hasattr(request.user, 'school_administrator'):
    groups = models.UserGroup.objects.all().filter(teacher__school=request.user.school_administrator.school).order_by('id')
  elif hasattr(request.user, 'teacher'):
    groups = models.UserGroup.objects.all().filter(teacher=request.user.teacher).order_by('id')
  else:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to view student groups</h1>')
  uploadForm = forms.UploadFileForm(user=request.user)
  context = {'groups': groups, 'role':'groups', 'uploadForm': uploadForm}
  return render(request, 'ctstem_app/UserGroups.html', context)


####################################
# CREATE MODIFY A USER GROUP
####################################
@login_required
def group(request, id=''):
  try:
    # check if the user has permission to create or modify a group
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'school_administrator') == False and hasattr(request.user, 'teacher') == False :
      return http.HttpResponseNotFound('<h1>You do not have the privilege to create/modify a group</h1>')
    # check if the lesson exists
    if '' != id:
      group = models.UserGroup.objects.get(id=id)
      if hasattr(request.user, 'teacher'):
        if request.user.teacher != group.teacher:
          return http.HttpResponseNotFound('<h1>You do not have the privilege to view/modify this group</h1>')
      elif hasattr(request.user, 'school_administrator'):
        if request.user.school_administrator.school != group.teacher.school:
          return http.HttpResponseNotFound('<h1>You do not have the privilege to view/modify this group</h1>')
    else:
      group = models.UserGroup()

    if request.method == 'GET':
        form = forms.UserGroupForm(user=request.user, instance=group, prefix='group')
        assignmentFormset=inlineformset_factory(models.UserGroup, models.Assignment, form=forms.AssignmentForm, can_delete=True, extra=1)
        formset = assignmentFormset(instance=group, prefix='form')
        uploadForm = forms.UploadFileForm(user=request.user)
        assignmentForm = forms.AssignmentSearchForm()
        studentSearchForm = forms.StudentSearchForm()
        studentAddForm = forms.StudentAddForm()
        context = {'form': form, 'formset': formset, 'role': 'group', 'uploadForm': uploadForm, 'assignmentForm': assignmentForm, 'studentSearchForm': studentSearchForm, 'studentAddForm': studentAddForm}
        return render(request, 'ctstem_app/UserGroup.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      #print data
      form = forms.UserGroupForm(user=request.user, data=data, instance=group, prefix="group")
      assignmentFormset=inlineformset_factory(models.UserGroup, models.Assignment, form=forms.AssignmentForm, can_delete=True, extra=1)
      formset = assignmentFormset(data, instance=group, prefix='form')
      if form.is_valid() and formset.is_valid():
        savedGroup = form.save()
        formset.save()
        id_list = []
        for key in data:
          if 'student_' in key:
            id_list.append(data[key])
        _do_action(request, id_list, 'student', id)
        messages.success(request, "Group Saved.")
        return shortcuts.redirect('ctstem:group', id=savedGroup.id)
      else:
        print form.errors
        print formset.errors
        messages.error(request, "The group could not be saved because there were errors.  Please check the errors below.")
        uploadForm = forms.UploadFileForm(user=request.user)
        assignmentForm = forms.AssignmentSearchForm()
        studentSearchForm = forms.StudentSearchForm()
        studentAddForm = forms.StudentAddForm()
        context = {'form': form, 'formset':formset, 'role': 'group', 'uploadForm': uploadForm, 'assignmentForm': assignmentForm, 'studentSearchForm': studentSearchForm, 'studentAddForm': studentAddForm}
        return render(request, 'ctstem_app/UserGroup.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.UserGroup.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested group not found</h1>')

####################################
# Search Assignment
####################################
@login_required
def searchAssignment(request):
  # check if the user has permission to add a question
  if hasattr(request.user, 'school_administrator') == False and hasattr(request.user, 'teacher') == False and  hasattr(request.user, 'administrator') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege search assignments</h1>')

  if 'POST' == request.method:
    data = request.POST.copy()
    query_filter = {}
    if data['curriculum_type']:
      query_filter['curriculum_type'] = str(data['curriculum_type'])
    if data['title']:
      query_filter['title__icontains'] = str(data['title'])
    if data['subject']:
      query_filter['subject__id'] = data['subject']

    query_filter['status'] = 'P'
    curriculumQueryset = models.Curriculum.objects.filter(**query_filter)
    curriculumList = []
    if data['curriculum_type'] == 'U':
      for curriculum in curriculumQueryset:
        if curriculum.underlying_curriculum.all().filter(status='P').count() > 0:
          curriculumList.append(curriculum)
    else:
      curriculumList = curriculumQueryset
    curriculum_list = [{'curriculum_type': curriculum.get_curriculum_type_display(), 'title': curriculum.title, 'subject': [subject.name for subject in curriculum.subject.all()], 'id': curriculum.id} for curriculum in curriculumList]
    return http.HttpResponse(json.dumps(curriculum_list), content_type="application/json")

  return http.HttpResponseNotAllowed(['POST'])

####################################
# Get underlying lessons when assigning a Unit
####################################
@login_required
def underlyingCurriculum(request, id=''):
  if hasattr(request.user, 'school_administrator') == False and hasattr(request.user, 'teacher') == False and  hasattr(request.user, 'administrator') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege search assignments</h1>')

  if 'GET' == request.method:
    curriculum = models.Curriculum.objects.get(id=id)
    underlying_curriculum = curriculum.underlying_curriculum.all().filter(status='P')
    curriculum_list = [{'id': curr.id, 'title': curr.title} for curr in underlying_curriculum]
    print curriculum_list
    return http.HttpResponse(json.dumps(curriculum_list), content_type="application/json")

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
      elif hasattr(request.user, 'school_administrator') and request.user.school_administrator.school == group.teacher.school:
        privilege = 1
      elif hasattr(request.user, 'teacher') and group.teacher == request.user.teacher:
        privilege = 1

      if privilege == 0:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to delete this group</h1>')

      if request.method == 'GET' or request.method == 'POST':
        group.delete()
        messages.success(request, 'Student Group "%s" deleted' % group.title)
        return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
      raise models.UserGroup.DoesNotExist

  except models.UserGroup.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested group not found</h1>')

####################################
# Group Dashboard
####################################
@login_required
def groupDashboard(request, id=''):
  try:
    if request.method == 'GET':
      group = models.UserGroup.objects.get(id=id)

      privilege = 1
      if hasattr(request.user, 'administrator') or hasattr(request.user, 'researcher'):
        privilege = 1
      elif hasattr(request.user, 'school_administrator'):
        if group.teacher.school != request.user.school_administrator.school:
          privilege = 0
      elif hasattr(request.user, 'teacher'):
        if group.teacher != request.user.teacher:
          privilege = 0
      else:
        privilege = 0

      if privilege == 0:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to view this group</h1>')

      assignments = {}
      serial = 0
      status_map = {'N': 'New', 'P': 'In Progress', 'S': 'Submitted', 'F': 'Feedback Ready', 'A': 'Archived'}
      status_color = {'N': 'gray', 'P': 'blue', 'S': 'green', 'F': 'orange', 'A': 'black'}
      assignment_queryset = models.Assignment.objects.all().filter(group=group)

      for assignment in models.Assignment.objects.all().filter(group=group):
        students = assignment.group.members.all()
        instances = models.AssignmentInstance.objects.all().filter(assignment=assignment)
        curriculum = models.Curriculum.objects.get(id=assignment.curriculum.id)
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
        for key, value in assignment_status.items():
          status.append({'name': status_map[key], 'y': value, 'color': status_color[key]})
        serial += 1

        if curriculum.curriculum_type == 'L' and curriculum.unit is not None:
          key = curriculum.unit
        else:
          key = curriculum

        if key in assignments:
          assignments[key].append({'assignment': assignment, 'status': status, 'serial': serial})
        else:
            assignments[key] = [{'assignment': assignment, 'status': status, 'serial': serial}]

      context = {'group': group, 'assignments': assignments}
      return render(request, 'ctstem_app/GroupDashboard.html', context)

    return http.HttpResponseNotAllowed(['GET'])

  except models.UserGroup.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested group not found</h1>')

####################################
# Assignment Dashboard
####################################
@login_required
def assignmentDashboard(request, id=''):
  try:
    if request.method == 'GET':
      assignment = models.Assignment.objects.get(id=id)

      privilege = 1
      if hasattr(request.user, 'administrator') or hasattr(request.user, 'researcher'):
        privilege = 1
      elif hasattr(request.user, 'school_administrator'):
        if assignment.group.teacher.school !=  request.user.school_administrator.school:
          privilege = 0
      elif hasattr(request.user, 'teacher'):
        if assignment.group.teacher != request.user.teacher:
          privilege = 0
      else:
        privilege = 0

      if privilege == 0:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to view this grassignmentoup</h1>')

      students = assignment.group.members.all()
      instances = models.AssignmentInstance.objects.all().filter(assignment=assignment)
      student_assignment_details = {}
      serial = 1
      for student in students:
        try:
          instance = instances.get(student=student)
          total_questions = models.CurriculumQuestion.objects.all().filter(step__curriculum=assignment.curriculum).count()
          attempted_questions = models.QuestionResponse.objects.all().filter(step_response__instance=instance).exclude(response__exact='', responseFile__exact='').count()
          total_steps = instance.assignment.curriculum.steps.count()
          last_step = instance.last_step
          if total_questions > 0:
            percent_complete = float(attempted_questions)/float(total_questions)*100
          else:
            percent_complete = float(last_step)/float(total_steps)*100

        except models.AssignmentInstance.DoesNotExist:
          instance = None
          percent_complete = 0

        student_assignment_details[student] = {'serial': serial, 'instance': instance, 'percent_complete': percent_complete}
        serial += 1

      context = {'assignment': assignment, 'student_assignment_details': student_assignment_details}
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
      assignments = models.Assignment.objects.all().filter(group__in=groups, assigned_date__lt=tomorrow)
      assignment_list = []
      active_list = []
      archived_list = []
      new_count = 0
      serial = 1
      percent_complete = 0
      for assignment in assignments:
        try:
          instance = models.AssignmentInstance.objects.get(assignment=assignment, student=student)

          if instance.status in ['N', 'P', 'S', 'F']:
            total_questions = models.CurriculumQuestion.objects.all().filter(step__curriculum=assignment.curriculum).count()
            attempted_questions = models.QuestionResponse.objects.all().filter(step_response__instance=instance).exclude(response__exact='', responseFile__exact='').count()
            total_steps = instance.assignment.curriculum.steps.count()
            last_step = instance.last_step

            print total_questions, attempted_questions, total_steps, last_step
            if instance.status == 'N':
              status = 1
              percent_complete = 0
            elif instance.status == 'P':
              status = 2
              if total_questions > 0:
                percent_complete = float(attempted_questions)/float(total_questions)*100
              else:
                percent_complete = float(last_step)/float(total_steps)*100
              print percent_complete
            elif instance.status == 'S':
              status = 3
              percent_complete = 100
            else:
              status = 4
              percent_complete = 100
            active_list.append({'serial': serial, 'assignment': assignment, 'instance': instance, 'percent_complete': percent_complete, 'status': status, 'modified_date': instance.modified_date})
          else:
            archived_list.append({'serial': serial, 'assignment': assignment, 'instance': instance, 'percent_complete': 100, 'status': 5, 'modified_date': instance.modified_date})
        except models.AssignmentInstance.DoesNotExist:
          instance = None
          new_count += 1
          active_list.append({'serial': serial, 'assignment': assignment, 'instance': instance, 'percent_complete': 0, 'status': 1, 'modified_date': timezone.now()})
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

      print sort_by
      if sort_by == 'assigned':
        assignment_list.sort(key=lambda item:item['assignment'].assigned_date)
      elif sort_by == 'group':
        assignment_list.sort(key=lambda item:item['assignment'].group)
      elif sort_by == 'due':
        assignment_list.sort(key=lambda item:item['assignment'].due_date)
      elif sort_by == 'status':
        assignment_list.sort(key=lambda item:item['status'])
      elif sort_by == 'percent':
        assignment_list.sort(key=lambda item:item['percent_complete'])
      elif sort_by == 'modified':
        assignment_list.sort(key=lambda item:item['modified_date'])

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
# STUDENT ATTEMPTING ASSIGNMENTS
####################################
@login_required
def assignment(request, assignment_id='', instance_id='', step_order=''):
  try:
    if hasattr(request.user, 'student') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to do this assignments</h1>')

    print assignment_id, instance_id, step_order
    #resuming/viewing assignment
    if '' != instance_id:
      instance = models.AssignmentInstance.objects.get(assignment_id=assignment_id, id=instance_id, student=request.user.student)
      if request.user.student != instance.student:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to do this assignments</h1>')
      last_step = instance.last_step
      #prevent users from manipulating the url in the browser
      if int(step_order) > last_step + 1:
        messages.error(request, 'Please use the buttons below to navigate between steps')
        return shortcuts.redirect('ctstem:resumeAssignment', assignment_id=assignment_id, instance_id=instance.id, step_order=last_step)

    #starting a new assignment
    else:
      instance = models.AssignmentInstance(assignment_id=assignment_id, student=request.user.student, status='N')
      instance.save()
      step_order = 0

    assignment = models.Assignment.objects.get(id=assignment_id)
    curriculum = assignment.curriculum

    if 'GET' == request.method or 'POST' == request.method:
      steps = models.Step.objects.all().filter(curriculum=curriculum)
      total_steps = steps.count()
      if int(step_order) == 0:
        attachments = models.Attachment.objects.all().filter(curriculum=curriculum, teacher_only=False)
        context = {'curriculum': curriculum, 'instance': instance, 'total_steps': total_steps, 'step_order': step_order, 'attachments': attachments}
        return render(request, 'ctstem_app/AssignmentStep.html', context)
      else:
        step = steps.get(order=step_order)
        initial_data = []

        try:
          assignmentStepResponse = models.AssignmentStepResponse.objects.get(instance=instance, step=step)
          extra = 0
        except models.AssignmentStepResponse.DoesNotExist:
          #unsaved object
          assignmentStepResponse = models.AssignmentStepResponse(instance=instance, step=step)
          curriculumQuestions = models.CurriculumQuestion.objects.all().filter(step=step).order_by('order')
          extra = curriculumQuestions.count()
          for curriculumQuestion in curriculumQuestions:
            initial_data.append({'curriculum_question': curriculumQuestion.id, 'response': ''})

        #get notes
        try:
          notes = models.AssignmentNotes.objects.get(instance=instance)
        except models.AssignmentNotes.DoesNotExist:
          notes = models.AssignmentNotes(instance=instance)

        if 'GET' == request.method:
          #get the assignment step
          form = forms.AssignmentStepResponseForm(instance=assignmentStepResponse, prefix="step_response")
          questionResponseFormset = nestedformset_factory(models.AssignmentStepResponse, models.QuestionResponse, form=forms.QuestionResponseForm,
                                                    nested_formset=inlineformset_factory(models.QuestionResponse, models.QuestionResponseFile, form=forms.QuestionResponseFileForm, can_delete=True, extra=2),
                                                    can_delete=False, can_order=True, extra=extra)

          #questionResponseFormset=inlineformset_factory(models.AssignmentStepResponse, models.QuestionResponse, form=forms.QuestionResponseForm, can_delete=False, can_order=True, extra=extra)
          formset = questionResponseFormset(instance=assignmentStepResponse, prefix='form')

          if int(step_order) == 1 and assignment.curriculum.curriculum_type == 'L':
            instanceform = forms.AssignmentInstanceForm(assignment=assignment, instance=instance, prefix="teammates")
          else:
            instanceform = None

          notesform = forms.AssignmentNotesForm(instance=notes, prefix="notes")

          if len(initial_data):
            for subform, data in zip(formset.forms, initial_data):
              subform.initial = data

          if instance.status == 'N' or instance.status == 'P':
            instance.save()
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
            assignmentStepResponse = form.save(commit=False)
            assignmentStepResponse.instance = instance
            assignmentStepResponse.save()

            questionCount = 0
            if request.is_ajax():
              formset.save(commit=False)
              questionResponses = {}
              # get the question response ids to update the front end
              for questionform in formset:
                questionCount = questionCount + 1
                # if questionResponse.curriculum_question.question.answer_field_type == 'SK':
                #   if questionResponse.response is not None and questionResponse.response != '':
                #     base64String = questionResponse.response.split(',')[1]
                #     sketch = base64.b64decode(base64String)
                #     image = ContentFile(sketch, 'sketch.png')
                #     questionResponse.responseFile = image
                #     questionResponse.response = None
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
              messages.success(request, 'Your assignment has been submitted')
              return shortcuts.redirect('ctstem:assignments', bucket='inbox')
            #Save or Save & Continue
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
            print form.errors
            print formset.errors
            print 'total errors', formset.total_error_count
            for f in formset.forms:
              print 'subform error', f.errors
              print 'subform non field error', f.non_field_errors

            messages.error(request, 'Please answer all non-optional questions on this step before continuing on to the next step')

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
      privilege = 0
      if hasattr(request.user, 'researcher') or hasattr(request.user, 'administrator'):
        privilege = 1
      elif hasattr(request.user, 'teacher') and request.user.teacher == group.teacher:
          privilege = 1
      elif hasattr(request.user, 'school_administrator') and request.user.school_administrator.school == school:
        privilege = 1

      if privilege == 0:
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
        print data
        form = forms.FeedbackForm(data, instance=feedback, prefix='feedback')
        #AssessmentStepFormSet = inlineformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,can_delete=True, can_order=True, extra=1)

        StepFeedbackFormSet = nestedformset_factory(models.AssignmentFeedback, models.StepFeedback, form=forms.StepFeedbackForm,
                                                      nested_formset=inlineformset_factory(models.StepFeedback, models.QuestionFeedback, form=forms.QuestionFeedbackForm, can_delete=False, can_order=False, extra=0),
                                                      can_delete=False, can_order=False, extra=0)


        formset = StepFeedbackFormSet(data, instance=feedback, prefix='form')
        print form.is_valid()
        print formset.is_valid()
        if form.is_valid() and formset.is_valid():
          form.save()
          formset.save()

          if data['save_and_send'] == 'true':
            instance.status = 'F'
            instance.save()
            messages.success(request, 'Your feedback has been saved and sent to the student')
            #notify student via email that feedback is ready
            send_feedback_ready_email(instance.student.user.email, instance.assignment.curriculum)
            #return shortcuts.redirect('ctstem:assignmentDashboard', id=assignment_id)
          else:
            messages.success(request, 'Your feedback has been saved')
        else:
          print form.errors
          print formset.errors
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
# Export Student Responses
####################################
@login_required
def export_response(request, assignment_id='', student_id=''):
  # check if the user has permission to add a question
  if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False and hasattr(request.user, 'teacher') == False and hasattr(request.user, 'school_administrator') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to export student response</h1>')
  try:
    assignment = models.Assignment.objects.get(id=assignment_id)
    if hasattr(request.user, 'school_administrator'):
      if assignment.group.teacher.school !=  request.user.school_administrator.school:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to export student responses for this assignment</h1>')
    elif hasattr(request.user, 'teacher'):
      if assignment.group.teacher != request.user.teacher:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to export student responses for this assignment</h1>')

    response = http.HttpResponse(content_type='application/ms-excel')
    if '' != student_id:
      student = models.Student.objects.get(id=student_id)
      instances = models.AssignmentInstance.objects.all().filter(assignment=assignment, student=student)
      response['Content-Disposition'] = 'attachment; filename="%s-%s.xls"'% (assignment, student)
    else:
      instances = models.AssignmentInstance.objects.all().filter(assignment=assignment)
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

    ws.write(row_num, 0, 'Group', bold_font_style)
    ws.write(row_num, 1, assignment.group.title, font_style)
    row_num += 1
    ws.write(row_num, 0, 'Assignment', bold_font_style)
    ws.write(row_num, 1, assignment.curriculum.title, font_style)
    row_num += 1
    ws.write(row_num, 0, 'Assigned Date', bold_font_style)
    ws.write(row_num, 1, assignment.assigned_date.replace(tzinfo=None), date_format)
    row_num += 1
    ws.write(row_num, 0, 'Due Date', bold_font_style)
    ws.write(row_num, 1, assignment.due_date.replace(tzinfo=None), date_format)
    row_num += 1
    ws.write(row_num, 0, '')

    columns = ['Student', 'Step No.', 'Step Title', 'Question No.', 'Question', 'Options', 'Correct Answer', 'Student Response', 'Submission DateTime']
    font_styles = [font_style, font_style, font_style, font_style, font_style, font_style, font_style, font_style, date_time_format]

    row_num += 1
    for col_num in range(len(columns)):
      ws.write(row_num, col_num, columns[col_num], bold_font_style)

    '''writer = csv.writer(response)
    writer.writerow(['Group', assignment.group])
    writer.writerow(['Assignment', assignment])
    writer.writerow(['Assigned Date', assignment.assigned_date])
    writer.writerow(['Due Date', assignment.due_date])
    writer.writerow([])
    writer.writerow(['Student', 'Step Title', 'Question', 'Options', 'Response'])'''

    for instance in instances:
      if hasattr(request.user, 'researcher'):
        student = instance.student.user.id
      else:
        student = instance.student.user.get_full_name()
      stepResponses = models.AssignmentStepResponse.objects.all().filter(instance=instance)
      for stepResponse in stepResponses:
        questionResponses = models.QuestionResponse.objects.all().filter(step_response=stepResponse)
        for questionResponse in questionResponses:
          response_text = get_response_text(request, instance.id, questionResponse)
          row = [student,
                 stepResponse.step.order,
                 stepResponse.step.title,
                 questionResponse.curriculum_question.order,
                 smart_str(questionResponse.curriculum_question.question),
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

    columns = ['Group', 'Curriculum', 'Assigned Date', 'Due Date', 'Student', 'Step No.', 'Step Title', 'Question No.', 'Question', 'Options', 'Correct Answer', 'Student Response', 'Submission DateTime']
    font_styles = [font_style, font_style, date_format, date_format, font_style, font_style, font_style, font_style, font_style, font_style, font_style, font_style, date_time_format]

    curricula = []

    if curriculum.curriculum_type != 'U':
      curricula.append(curriculum)
    else:
      curricula = curriculum.underlying_curriculum.all().filter(Q(status='P')|Q(status='A'))

    for curr in curricula:
      if hasattr(request.user, 'administrator') == True or hasattr(request.user, 'researcher') == True:
        assignments = models.Assignment.objects.all().filter(curriculum__id = curr.id)
      elif hasattr(request.user, 'school_administrator') == True:
        assignments = models.Assignment.objects.all().filter(curriculum__id = curr.id, group__teacher__school = request.user.school_administrator.school)
      elif hasattr(request.user, 'teacher') == True:
        assignments = models.Assignment.objects.all().filter(curriculum__id = curr.id, group__teacher = request.user.teacher)
      else:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to export student response for the selected curriculum</h1>')

      instances = models.AssignmentInstance.objects.all().filter(assignment__in=assignments)
      sheet_title = curr.title
      for ch in "[]:*?/\\":
        if ch in curr.title:
          sheet_title = sheet_title.replace(ch, "-")

      #truncate sheet_title to 30 characters
      sheet_title = (sheet_title[:30]) if len(sheet_title) > 30 else sheet_title

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
          stepResponses = models.AssignmentStepResponse.objects.all().filter(instance=instance)
          print stepResponses
          for stepResponse in stepResponses:
            questionResponses = models.QuestionResponse.objects.all().filter(step_response=stepResponse)
            for questionResponse in questionResponses:
              response_text = get_response_text(request, instance.id, questionResponse)
              row = [instance.assignment.group.title,
                     instance.assignment.curriculum.title,
                     instance.assignment.assigned_date.replace(tzinfo=None),
                     instance.assignment.due_date.replace(tzinfo=None),
                     student,
                     stepResponse.step.order,
                     stepResponse.step.title,
                     questionResponse.curriculum_question.order,
                     smart_str(questionResponse.curriculum_question.question),
                     smart_str(questionResponse.curriculum_question.question.options),
                     smart_str(questionResponse.curriculum_question.question.answer),
                     response_text,
                     questionResponse.modified_date.replace(tzinfo=None)]
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
    response_text = 'http://%s/response/%d/%d'%(domain, instance_id, questionResponse.id)
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
  if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False and hasattr(request.user, 'author') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to add a question</h1>')
  if '' == id:
    question = models.Question()
    title = 'Add Question'
  else:
    question = models.Question.objects.get(id=id)
    title = 'Edit Question'

  if 'GET' == request.method:
    questionForm = forms.QuestionForm(instance=question)
    context = {'questionForm': questionForm, 'title': title}
    return render(request, 'ctstem_app/Question.html', context)

  elif 'POST' == request.method:
    data = request.POST.copy()
    print data
    questionForm = forms.QuestionForm(data, request.FILES, instance=question)
    if questionForm.is_valid():
      question = questionForm.save()
      response_data = {'question_id': question.id, 'question_text': question.question_text}
      return http.HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
      print questionForm.errors
      response_data = {'error': 'Required fields are missing'}
      return http.HttpResponse(json.dumps(response_data), content_type="application/json")

  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# Display the question response based on the answer field type
####################################
def questionResponse(request, instance_id='', response_id=''):
  try:
    if request.user.is_anonymous():
      messages.info(request, 'Please login to view the link')
      return shortcuts.redirect('ctstem:home')
    # check if the user has permission to view student response
    if '' != instance_id and '' != response_id:
      instance = models.AssignmentInstance.objects.get(id=instance_id)
      print 'instance', instance
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
        print 'response', question_response
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
  code = generate_code_helper(request)
  response_data = {'code': code}
  return http.HttpResponse(json.dumps(response_data), content_type="application/json")

####################################
# GENERATE UNIQUE USER CODE HELPER
####################################
def generate_code_helper(request):
  allowed_chars = ''.join((string.uppercase, string.digits))
  code = get_random_string(length=5, allowed_chars=allowed_chars)
  schools = models.School.objects.all().filter(school_code=code)
  # ensure the user code is unique across teachers and researchers
  while schools.count() > 0:
    code = get_random_string(length=5, allowed_chars=allowed_chars)
    schools = models.School.objects.all().filter(school_code=code)

  return code

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
    form = forms.UploadFileForm(request.POST, user=request.user)
    data = request.POST.copy()
    if form.is_valid():
      group = models.UserGroup.objects.get(id=data['group'])
      emails = data['emails'].split(",")
      for email in emails:
        count += 1
        #check email format
        try:
          validate_email(email)
          valid_email = True
        except ValidationError:
          valid_email = False

        if not valid_email:
          msg['error'].append('Email %d is invalid' % count)
          messages.error(request, 'Email %d is invalid' % count)
          invalid +=1
        else:
          #check if email exists
          if User.objects.filter(email=email).exists():
            #check if email belongs to a student
            if models.Student.objects.filter(user__email=email).exists():
              #add student to group
              #TODO
              student = models.Student.objects.get(user__email=email)
              membership, created = models.Membership.objects.get_or_create(student=student, group=group)
              added_students[student.id] = {'user_id': student.user.id, 'username': student.user.username, 'full_name': student.user.get_full_name(), 'email': student.user.email, 'status': 'Active' if student.user.is_active else 'Inactive', 'last_login': student.user.last_login.strftime('%B %d, %Y') if student.user.last_login else '', 'group': group.id}
              added += 1
            else:
              #error out email in use and does not belong to a student account
              msg['error'].append('Email %d does not belong to a student account' % count)
              messages.error(request, 'Email %d does not belong to a student account' % count)
              invalid += 1
          else:
            #email does not exist.  Send and email with registration link
            send_account_creation_email(email, group)
            new += 1

      if added:
        msg['success'].append('Existing students added to the group: %d' % (added))
        messages.success(request, 'Existing students added to the group: %d' % (added))
      if new:
        msg['success'].append('Email sent to new students to create an account: %d' % (new))
        messages.success(request, 'Email sent to new students to create an account: %d' % (new))
      if invalid:
        msg['error'].append('Invalid emails found: %d' % (invalid))
        messages.error(request, 'Invalid emails found: %d' % (invalid))

      response_data = {'result': 'Success', 'new_students': added_students, 'messages': msg}
    else:
      print form.errors
      response_data = {'result': 'Failure', 'message': 'Please select a group and a comma separated list of student emails to upload.'}
    return http.HttpResponse(json.dumps(response_data), content_type="application/json")

  return http.HttpResponseNotAllowed(['POST'])

####################################
# UPLOAD USERS
####################################

# @login_required
# def user_upload_csv(request):
#   if hasattr(request.user, 'administrator'):
#     role = 'admin'
#   elif hasattr(request.user, 'school_administrator'):
#     role = 'school_administrator'
#   elif hasattr(request.user, 'teacher'):
#     role = 'teacher'
#   else:
#     return http.HttpResponseNotFound('<h1>You do not have the privilege to upload users</h1>')

#   count = 0
#   added = 0
#   new = 0
#   added_students = {}
#   msg = {'error': [], 'success': []}

#   if request.method == 'POST':
#     form = forms.UploadFileForm(request.POST, request.FILES, user=request.user)
#     data = request.POST.copy()
#     print data
#     if form.is_valid():
#       f = request.FILES['uploadFile']
#       group = models.UserGroup.objects.get(id=data['group'])
#       reader = csv.reader(f.read().splitlines(), delimiter=',')
#       for row in reader:
#         count += 1
#         if row[0] != 'Email*':
#           email = str(row[0])
#           print email

#           #check if the student with the email already exists
#           #email is mandatory
#           if email is None or email == '':
#             msg['error'].append('Email is missing on row %d' % count)
#             messages.error(request, 'Email is missing on row %d' % count)
#           else:
#             #check if email exists
#             if User.objects.filter(email=email).exists():
#               #check if email belongs to a student
#               if models.Student.objects.filter(user__email=email).exists():
#                 #add student to group
#                 #TODO
#                 student = models.Student.objects.get(user__email=email)
#                 membership, created = models.Membership.objects.get_or_create(student=student, group=group)
#                 added_students[student.id] = {'user_id': student.user.id, 'username': student.user.username, 'full_name': student.user.get_full_name(), 'email': student.user.email, 'status': 'Active' if student.user.is_active else 'Inactive', 'last_login': student.user.last_login.strftime('%B %d, %Y') if student.user.last_login else '', 'group': group.id}
#                 added += 1
#               else:
#                 #error out email in use and does not belong to a student account
#                 msg['error'].append('Email on row %d does not belong to a student account' % count)
#                 messages.error(request, 'Email on row %d does not belong to a student account' % count)
#             else:
#               #email does not exist.  Send and email with registration link
#               send_account_creation_email(email, group)
#               new += 1


#       msg['success'].append('%d existing students were found and added to the group, %d new students were requested to create an account.' % (added, new))
#       messages.success(request, '%d existing students were found and added to the group, %d new students were requested to create an account.' % (added, new))
#       response_data = {'result': 'Success', 'new_students': added_students, 'messages': msg}
#     else:
#       print form.errors
#       response_data = {'result': 'Failure', 'message': 'Please select a group and provide a valid student template to upload.'}
#     return http.HttpResponse(json.dumps(response_data), content_type="application/json")

#   return http.HttpResponseNotAllowed(['POST'])


def send_account_confirmation_email(user, password):
  #email user the  user name and password
  current_site = Site.objects.get_current()
  domain = current_site.domain

  send_mail('CT-STEM Account Created',
  'Your student account has been created on Computational Thinking in STEM website http://%s.  \r\n\r\n \
   Please login to the site using the credentials below and change your password.\r\n  \
   Username: %s \r\n \
   Temporary Password: %s \r\n\r\n \
   -- CT-STEM Admin'%(domain, user.username, password),
        settings.DEFAULT_FROM_EMAIL,
        [user.email])

def send_account_creation_email(email, group):
  #email user the  user name and password
  current_site = Site.objects.get_current()
  domain = current_site.domain

  send_mail('CT-STEM Account Signup',
  'Your teacher has requested you to create an account on Computational Thinking in STEM website \r\n\r\n \
  Please click the link below to create an account.\r\n  \
  http://%s/register/group/%d?email=%s  \r\n\r\n \
  -- CT-STEM Admin'%(domain, group.id, email),
        settings.DEFAULT_FROM_EMAIL,
        [email])

def send_feedback_ready_email(email, curriculum):
  current_site = Site.objects.get_current()
  domain = current_site.domain

  send_mail('CT-STEM Assignment Feedback Ready',
  'Your teacher has provided feedback on the assignment %s. \r\n\r\n \
  Please login to our website http://%s to review the feedback. \r\n\r\n  \
  -- CT-STEM Admin'%(curriculum.title, domain),
        settings.DEFAULT_FROM_EMAIL,
        [email])

def send_account_validation_email(teacher):
  current_site = Site.objects.get_current()
  domain = current_site.domain

  send_mail('CT-STEM Account Validation',
    ' \r\n \
    Welcome to Computational Thinking in STEM \r\n\r\n \
    Please validate your account here http://%s/validate  and use the credentials below.\r\n\r\n \
    Username: %s \r\n\r\n \
    Validation code: %s \r\n\r\n \
    -- CT-STEM Admin' % (domain, teacher.user.username, teacher.validation_code),
              settings.DEFAULT_FROM_EMAIL,
              [teacher.user.email])

def send_account_approval_email(user):
  current_site = Site.objects.get_current()
  domain = current_site.domain

  send_mail('CT-STEM Account Approval',
  'Your account has been approved on Computational Thinking in STEM website http://%s.  \r\n\r\n \
   Please login to the site using the the credentials created during registration.\r\n\r\n  \
   -- CT-STEM Admin'%(domain) ,
              settings.DEFAULT_FROM_EMAIL,
              [user.email])

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
        print form.errors
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
      print school
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

      form = forms.SubjectForm(data, instance=subject, prefix="subject")
      if form.is_valid():
        form.save()
        messages.success(request, "Subject Saved.")
        return shortcuts.redirect('ctstem:subjects',)
      else:
        print form.errors
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
      print formset.errors
      context = {'formset': formset}
      return render(request, 'ctstem_app/TeamRoles.html', context)
  return http.HttpResponseNotAllowed(['GET', 'POST'])


@login_required
def teamMembers(request):
  if hasattr(request.user, 'administrator') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to edit team roles</h1>')

  members = models.Team.objects.all().order_by('order')
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
        print form.errors
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
def training(request):
  return render(request, 'ctstem_app/Training.html')


####################################
# LIST OF PROFESSIONAL DEVELOPMENT REQUESTS
####################################
@login_required
def training_requests(request):
  if hasattr(request.user, 'administrator') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to view this page</h1>')

  if request.method == "GET" or request.method == "POST":
    trainingRequests = models.TrainingRequest.objects.all()
    print trainingRequests
    context = {'trainingRequests': trainingRequests}
    return render(request, 'ctstem_app/TrainingRequests.html', context)
  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# RECORD PD REQUESTS
####################################
def request_training(request):

  training = models.TrainingRequest()
  if request.method == 'GET':
    if request.user.is_authenticated():
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
    #checking for bots
    if 'condition' in data:
      messages.success(request, "Your request has been sent to the site admin")
      response_data['result'] = 'Success'
      return http.HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
      form = forms.TrainingRequestForm(data, instance=training)
      if form.is_valid():
        training = form.save()
        messages.success(request, "Your request has been sent to the site admin")
        response_data['result'] = 'Success'
        #send email to the admin
        send_email('CT-STEM Training Request',
                    '<b>Name </b>: %s <br> \
                    <b>Email </b>: %s <br> \
                    <b>School </b>: %s <br> \
                    <b>Subject </b>: %s <br><br> \
                    Thank you for your interest in attending our training session.  We will communicate \
                    the date, place and other details about the event shortly. <br> \
                    <br> \
                    -CT-STEM Admin' % (training.name, training.email, training.school, training.subject),
                    settings.DEFAULT_FROM_EMAIL,
                    [training.email])
        return http.HttpResponse(json.dumps(response_data), content_type="application/json")
      else:
        print form.errors
        return JsonResponse({
            'result': 'Failed',
            'errors': dict(form.errors.items()),
        })

  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# Validate account
####################################
def validate(request):
  if request.method == 'GET':
    form = forms.ValidationForm()
    context = {'form': form}
    return render(request, 'ctstem_app/Validation.html', context)
  elif request.method == 'POST':
    data = request.POST.copy()
    form = forms.ValidationForm(data)
    if form.is_valid():
      username = form.cleaned_data['username']
      password = form.cleaned_data['password']
      user = authenticate(username=username, password=password)
      user.is_active = True
      user.save()
      #check if this user added a new school
      if hasattr(user, 'teacher'):
        school = models.School.objects.get(id=user.teacher.school.id)
        if not school.is_active:
          school.is_active = True
          school.save()

      login(request, user)
      messages.success(request, "Your account has been validated")
      return shortcuts.redirect('ctstem:home')
    else:
      context = {'form': form}
      return render(request, 'ctstem_app/Validation.html', context)


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
