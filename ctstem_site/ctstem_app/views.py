from django.http import HttpResponse
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
from django.db.models import Q
from django.core.files.base import ContentFile
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.sites.models import Site

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
    context = {'lessons': lessons, 'assessments' : assessments, 'practices': practices, 'team': team, 'publications': publications}
    return render(request, 'ctstem_app/Home.html', context)

####################################
# ABOUT US
####################################
def team(request):
  roles = models.TeamRole.objects.all()
  context = {'roles': roles}
  return render(request, 'ctstem_app/Team.html', context)

####################################
# Curricula TABLE VIEW
####################################
def curricula(request, curriculum_type='', bookmark='0'):
  if curriculum_type == 'assessments':
    curr_type = 'A'
  else:
    curr_type = 'L'

  bookmarked = None

  if hasattr(request.user, 'administrator') == True or hasattr(request.user, 'researcher') == True:
    curricula = models.Curriculum.objects.all().filter(curriculum_type = curr_type).order_by('id')
  elif hasattr(request.user, 'author') == True:
    curricula = models.Curriculum.objects.all().filter(Q(curriculum_type = curr_type), Q(status='P') | Q(author=request.user) ).order_by('id')
  elif hasattr(request.user, 'teacher') == True:
    if bookmark == '1':
      curricula = models.Curriculum.objects.all().filter(curriculum_type = curr_type, status='P', bookmarked__teacher=request.user.teacher).order_by('id')
      bookmarked = curricula
    else:
      curricula = models.Curriculum.objects.all().filter(curriculum_type = curr_type, status='P').order_by('id')
      bookmarked = curricula.filter(bookmarked__teacher=request.user.teacher)
  else:
    curricula = models.Curriculum.objects.all().filter(curriculum_type = curr_type, status='P').order_by('id')

  context = {'curricula': curricula, 'curriculum_type': curr_type, 'bookmark': bookmark, 'bookmarked': bookmarked}
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
      print form.is_valid()
      print formset.is_valid()
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
        messages.error(request, "The curriculum could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form, 'attachment_formset': attachment_formset, 'formset':formset, 'newQuestionForm': newQuestionForm}
        return render(request, 'ctstem_app/Curriculum.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested curriculum not found</h1>')

####################################
# PREVIEW A Curriculum
####################################
def previewCurriculum(request, id=''):
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
  return HttpResponse('We had some errors! %s' % escape(html))
####################################
# DELETE a curriculum
####################################
def deleteCurriculum(request, id=''):
  try:
    # check if the user has permission to delete a lesson
    if hasattr(request.user, 'administrator') == False:
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
    if hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to modify this curriculum</h1>')
    # check if the curriculum exists
    else:
      if request.method == 'GET' or request.method == 'POST':
        if '' != id:
          curriculum = models.Curriculum.objects.get(id=id)
          steps = models.Step.objects.all().filter(curriculum=curriculum)
          attachments = models.Attachment.objects.all().filter(curriculum=curriculum)
          title = curriculum.title
          curriculum.title = str(datetime.datetime.now())
          curriculum.slug = slugify(curriculum.title)
          curriculum.pk = None
          curriculum.id = None
          curriculum.save()

          original_curriculum = models.Curriculum.objects.get(id=id)
          curriculum.title = title
          curriculum.author = request.user
          curriculum.modified_by = request.user
          curriculum.created_date = datetime.datetime.now()
          curriculum.modified_date = datetime.datetime.now()
          curriculum.parent = original_curriculum
          curriculum.status = 'D'
          curriculum.version = int(original_curriculum.version) + 1
          curriculum.slug = slugify(curriculum.title) + '-v%s'%curriculum.version + '-%s'%curriculum.id
          curriculum.subject = original_curriculum.subject.all()
          curriculum.taxonomy = original_curriculum.taxonomy.all()

          filecontent = ContentFile(original_curriculum.icon.file.read())
          filename = os.path.split(original_curriculum.icon.file.name)[-1]
          filename_array = filename.split('.')
          filename = filename_array[0] + '-' + str(curriculum.id) + '.' + filename_array[1]
          curriculum.icon.save(filename, filecontent)
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

          for step in steps:
              step_questions = models.CurriculumQuestion.objects.all().filter(step=step)
              step.pk = None
              step.id = None
              step.curriculum = curriculum
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

          messages.success(request, "A new copy of %s created.  Please archive the original curriculum" % original_curriculum.title)
          return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))
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
      messages.success(request, 'Curriculum %s has been bookmarked' % curriculum.title)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
      messages.success(request, 'Bookmark on curriculum %s has been removed' % curriculum.title)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Curriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested curriculum not found</h1>')
  except models.BookmarkedCurriculum.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested bookmark not found</h1>')
####################################
# REGISTER
####################################
def register(request):
  if request.method == 'POST':
    form = forms.RegistrationForm(user=request.user, data=request.POST)
    if form.is_valid():
      user = User.objects.create_user(form.cleaned_data['username'],
                                      form.cleaned_data['email'],
                                      form.cleaned_data['password1'])
      user.first_name = form.cleaned_data['first_name']
      user.last_name = form.cleaned_data['last_name']
      if form.cleaned_data['account_type'] in  ['A', 'R', 'C'] and request.user.is_anonymous():
          user.is_active = False
      else:
          user.is_active = True
      user.save()

      if form.cleaned_data['account_type'] == 'T':
        newUser = models.Teacher()
        newUser.school = form.cleaned_data['school']
        newUser.user_code =  form.cleaned_data['user_code']
        newUser.user = user
        newUser.save()
        #get the school admin based on the permission code

        if request.user.is_authenticated() and hasattr(request.user, 'researcher'):
          request.user.researcher.teachers.add(newUser)
        elif form.cleaned_data['permission_code']:
          researcher = models.Researcher.objects.get(user_code = form.cleaned_data['permission_code'])
          researcher.teachers.add(newUser)

      elif form.cleaned_data['account_type'] == 'S':
        newUser = models.Student()
        newUser.school = form.cleaned_data['school']
        newUser.user = user
        newUser.save()
        #get the teacher based on the permission code
        if request.user.is_authenticated() and hasattr(request.user, 'teacher'):
          request.user.teacher.students.add(newUser)
        elif form.cleaned_data['permission_code']:
          teacher = models.Teacher.objects.get(user_code = form.cleaned_data['permission_code'])
          teacher.students.add(newUser)

      elif form.cleaned_data['account_type'] == 'A':
          newUser = models.Administrator()
          newUser.user = user
          newUser.save()

      elif form.cleaned_data['account_type'] == 'R':
        newUser = models.Researcher()
        newUser.school = form.cleaned_data['school']
        newUser.user_code =  form.cleaned_data['user_code']
        newUser.user = user
        newUser.save()
      elif form.cleaned_data['account_type'] == 'C':
        newUser = models.Author()
        newUser.user = user
        newUser.save()

      current_site = Site.objects.get_current()
      domain = current_site.domain

      if request.user.is_anonymous():
        if form.cleaned_data['account_type'] in ['A', 'R', 'C']:
          messages.info(request, 'Your account is pending admin approval.  You will be notified once your account is approved.')
          #send email confirmation
          send_mail('CT-STEM Account Pending',
                    'Welcome to Computational Thinking in STEM website http://%s.  \r\n\r\n \
                    Your account is pending approval, and you will be notified once approved.\r\n\r\n  \
                    -- CT-STEM Admin' % domain,
                    settings.DEFAULT_FROM_EMAIL,
                    [newUser.user.email])
          return shortcuts.redirect('ctstem:home')

        elif form.cleaned_data['account_type'] in ['T', 'S']:
          new_user = authenticate(username=form.cleaned_data['username'],
                                  password=form.cleaned_data['password1'], )
          login(request, new_user)
          messages.info(request, 'Your have successfully registered.')
          send_mail('CT-STEM Account Created',
                    'Welcome to Computational Thinking in STEM website %s.  \r\n\r\n \
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
        elif form.cleaned_data['account_type'] == 'C':
          return shortcuts.redirect('ctstem:users', role='authors')
        elif form.cleaned_data['account_type'] == 'T':
          return shortcuts.redirect('ctstem:users', role='teachers')
        elif form.cleaned_data['account_type'] == 'S':
          return shortcuts.redirect('ctstem:users', role='students')
        return render(request, 'ctstem_app/About_us.html')

    else:
      print form.errors
      context = {'form': form}
      return render(request, 'ctstem_app/Registration.html', context)

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
    elif hasattr(user, 'student'):
      role = 'student'
      student = models.Student.objects.get(user__id=id)
    elif hasattr(user, 'researcher'):
      role = 'researcher'
      researcher = models.Researcher.objects.get(user__id=id)
    elif hasattr(user, 'author'):
      role = 'author'
      author = models.Author.objects.get(user__id=id)
    else:
      return http.HttpResponseForbidden('<h1>User has no role</h1>')

    if request.method == 'GET':
      userform = forms.UserProfileForm(instance=user, prefix='user')
      if role in ['student', 'teacher', 'administrator', 'researcher', 'author']:
        if role == 'student':
          profileform = forms.StudentForm(instance=student, prefix='student')
        elif role == 'teacher':
          profileform = forms.TeacherForm(instance=teacher, prefix='teacher')
        elif role == 'administrator':
          profileform = None
        elif role == 'researcher':
          profileform = forms.ResearcherForm(instance=researcher, prefix='researcher')
        elif role == 'author':
          profileform = forms.AuthorForm(instance=author, prefix='author')
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
      data.__setitem__('user-password', user.password)
      data.__setitem__('user-last_login', user.last_login)
      data.__setitem__('user-date_joined', user.date_joined)
      userform = forms.UserProfileForm(data, instance=user, prefix='user')

      profileform = None
      if role == 'student':
        profileform = forms.StudentForm(data, instance=student, prefix='student')
      elif role == 'teacher':
        profileform = forms.TeacherForm(data, instance=teacher, prefix='teacher')
      elif role == 'researcher':
        profileform = forms.ResearcherForm(data, instance=researcher, prefix='researcher')
      elif role == 'author':
        profileform = forms.AuthorForm(data, instance=author, prefix='author')

      if userform.is_valid():
        if profileform is None:
          userform.save()
          messages.success(request, "User profile saved successfully")
          context = {'userform': userform, 'role': role}
        elif profileform.is_valid():
          userform.save()
          profileform.save()
          messages.success(request, "User profile saved successfully")
          context = {'profileform': profileform, 'userform': userform, 'role': role}
        else:
          print profileform.errors
          messages.error(request, "User profile could not be saved. Please check the errors below.")
          context = {'profileform': profileform, 'userform': userform, 'role': role}
      else:
        print profileform.errors
        print userform.errors
        messages.error(request, "User profile could not be saved. Please check the errors below.")
        context = {'profileform': profileform, 'userform': userform, 'role': role}

      return render(request, 'ctstem_app/UserProfile.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except User.DoesNotExist:
      return http.HttpResponseNotFound('<h1>Requested user not found</h1>')

####################################
# DELETE USER
####################################
def deleteUser(request, id=''):
  try:
    # check if the user has permission to delete a lesson
    if hasattr(request.user, 'author') or hasattr(request.user, 'student'):
      return http.HttpResponseNotFound('<h1>You do not have the privilege to delete users</h1>')
    # check if the lesson exists
    if '' != id:
      user = User.objects.get(id=id)

    if hasattr(request.user, 'researcher'):
      if hasattr(user, 'administrator') or hasattr(user, 'researcher') or hasattr(user, 'author'):
        return http.HttpResponseNotFound('<h1>You do not have the privilege to delete this user</h1>')
    if hasattr(request.user, 'teacher'):
      if hasattr(user, 'administrator') or hasattr(user, 'researcher') or hasattr(user, 'author') or hasattr(user, 'teacher'):
        return http.HttpResponseNotFound('<h1>You do not have the privilege to delete this user</h1>')

    if request.method == 'GET' or request.method == 'POST':
      user.delete()
      messages.success(request, '%s deleted' % user.username)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except User.DoesNotExist:
    return http.HttpResponseNotFound('<h1>User not found</h1>')


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
        for form in formset.ordered_forms:
          form.instance.order = form.cleaned_data['ORDER']
          form.save()
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
  if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False and hasattr(request.user, 'author') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege search taxonomy</h1>')

  subcategory = models.Subcategory()
  title = 'Search Taxonomy'
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
# USER LIST
####################################
@login_required
def users(request, role):

  if hasattr(request.user, 'administrator'):
    privilege = 10
  elif hasattr(request.user, 'researcher'):
    privilege = 7
  elif hasattr(request.user, 'teacher'):
    privilege = 5
  elif hasattr(request.user, 'student') or hasattr(request.user, 'author'):
    privilege = 1

  if role == 'students' and privilege > 1:
    users = models.Student.objects.all()
  elif role == 'teachers' and privilege > 5:
    users = models.Teacher.objects.all()
  elif role == 'admins' and privilege > 7:
    users = models.Administrator.objects.all()
  elif role == 'researchers' and privilege > 7:
    users = models.Researcher.objects.all()
  elif role == 'authors' and privilege > 7:
    users = models.Author.objects.all()
  else:
    return http.HttpResponseNotFound('<h1>You do not have the privilege view %s</h1>'% role)

  uploadForm = forms.UploadFileForm()
  context = {'users': users, 'role': role, 'uploadForm': uploadForm}
  return render(request, 'ctstem_app/Users.html', context)

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
  if hasattr(request.user, 'administrator'):
    groups = models.UserGroup.objects.all().order_by('id')
  elif hasattr(request.user, 'researcher'):
    subordinate_teachers = request.user.researcher.teachers.all()
    groups = models.UserGroup.objects.all().filter(teacher__in=subordinate_teachers).order_by('id')
  elif hasattr(request.user, 'teacher'):
    groups = models.UserGroup.objects.all().filter(teacher=request.user.teacher).order_by('id')
  else:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to view student groups</h1>')
  context = {'groups': groups, 'role':'groups'}
  return render(request, 'ctstem_app/UserGroups.html', context)


####################################
# CREATE MODIFY A USER GROUP
####################################
@login_required
def group(request, id=''):
  try:
    # check if the user has permission to create or modify a lesson
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False and hasattr(request.user, 'teacher') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to create/modify a group</h1>')
    # check if the lesson exists
    if '' != id:
      group = models.UserGroup.objects.get(id=id)
    else:
      group = models.UserGroup()

    if request.method == 'GET':
        form = forms.UserGroupForm(instance=group, prefix='group')
        assignmentFormset=inlineformset_factory(models.UserGroup, models.Assignment, form=forms.AssignmentForm, can_delete=True, extra=1)
        formset = assignmentFormset(instance=group, prefix='form')
        context = {'form': form, 'formset': formset, 'role': 'group'}
        return render(request, 'ctstem_app/UserGroup.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      print data
      form = forms.UserGroupForm(data, instance=group, prefix="group")
      assignmentFormset=inlineformset_factory(models.UserGroup, models.Assignment, form=forms.AssignmentForm, can_delete=True, extra=1)
      formset = assignmentFormset(data, instance=group, prefix='form')
      if form.is_valid() and formset.is_valid():
        savedGroup = form.save()
        formset.save()
        messages.success(request, "User Group Saved.")
        return shortcuts.redirect('ctstem:group', id=savedGroup.id)
      else:
        print form.errors
        print formset.errors
        messages.error(request, "The group could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form, 'formset':formset, 'role': 'group'}
        return render(request, 'ctstem_app/UserGroup.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.UserGroup.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested group not found</h1>')

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
      allowed = False
      if hasattr(request.user, 'administrator'):
        allowed = True
      elif hasattr(request.user, 'researcher'):
        subordinate_teachers = request.user.researcher.teachers.all()
        if group.teacher in subordinate_teachers:
          allowed = True
      elif hasattr(request.user, 'teacher') and group.teacher == request.user.teacher:
        allowed = True

      if allowed == False:
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

      if hasattr(request.user, 'administrator'):
        pass
      elif hasattr(request.user, 'researcher'):
        subordinate_teachers = request.user.researcher.teachers.all()
        if group.teacher not in subordinate_teachers:
          return http.HttpResponseNotFound('<h1>You do not have the privilege to view this group</h1>')
      elif hasattr(request.user, 'teacher'):
        if group.teacher != request.user.teacher:
          return http.HttpResponseNotFound('<h1>You do not have the privilege to view this group</h1>')
      else:
        return http.HttpResponseNotFound('<h1>You do not have the privilege to view this group</h1>')

      assignments = []
      serial = 0
      status_map = {'N': 'New', 'P': 'In Progress', 'S': 'Submitted', 'F': 'Feedback Ready', 'A': 'Archived'}
      status_color = {'N': 'gray', 'P': 'blue', 'S': 'green', 'F': 'orange', 'A': 'black'}
      for assignment in models.Assignment.objects.all().filter(group=group):
        students = assignment.group.members.all()
        instances = models.AssignmentInstance.objects.all().filter(assignment=assignment)
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
        assignments.append({'assignment': assignment, 'status': status, 'serial': serial})
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

      if hasattr(request.user, 'administrator'):
        pass
      elif hasattr(request.user, 'researcher'):
        subordinate_teachers = request.user.researcher.teachers.all()
        if assignment.group.teacher not in subordinate_teachers:
          return http.HttpResponseNotFound('<h1>You do not have the privilege to view this assignment</h1>')
      elif hasattr(request.user, 'teacher'):
        if assignment.group.teacher != request.user.teacher:
          return http.HttpResponseNotFound('<h1>You do not have the privilege to view this assignment</h1>')
      else:
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
          percent_complete =  float(attempted_questions)/float(total_questions)*100
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
      assignments = models.Assignment.objects.all().filter(group__in=groups)
      assignment_list = []
      active_list = []
      archived_list = []
      new_count = 0
      serial = 1
      for assignment in assignments:
        try:
          instance = models.AssignmentInstance.objects.get(assignment=assignment, student=student)
          if instance.status in ['P', 'S', 'F']:
            total_questions = models.CurriculumQuestion.objects.all().filter(step__curriculum=assignment.curriculum).count()
            attempted_questions = models.QuestionResponse.objects.all().filter(step_response__instance=instance).exclude(response__exact='', responseFile__exact='').count()
            if instance.status == 'P':
              status = 2
            elif instance.status == 'S':
              status = 3
            else:
              status = 4
            active_list.append({'serial': serial, 'assignment': assignment, 'instance': instance, 'percent_complete': float(attempted_questions)/float(total_questions)*100, 'status': status, 'modified_date': instance.modified_date})
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

      context = {'assignment_list': assignment_list, 'new': new_count, 'inbox': len(active_list), 'archived': len(archived_list), 'sort_form': sort_form}
      return render(request, 'ctstem_app/MyAssignments.html', context)
    return http.HttpResponseNotAllowed(['GET'])

  except models.Student.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested student not found</h1>')

####################################
# STUDENT archives assignment
####################################
@login_required
def archiveAssignment(request, instance_id=''):
  try:
    if hasattr(request.user, 'student') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to archive this assignments</h1>')

    instance = models.AssignmentInstance.objects.get(id=instance_id)
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
      last_step = instance.last_step
      #prevent users from manipulating the url in the browser
      if int(step_order) > last_step + 1:
        messages.error(request, 'Please use the buttons below to navigate between steps')
        return shortcuts.redirect('ctstem:resumeAssignment', assignment_id=assignment_id, instance_id=instance.id, step_order=last_step)
      if int(step_order) == 0:
        step_order = 1
    #starting a new assignment
    else:
      instance = models.AssignmentInstance(assignment_id=assignment_id, student=request.user.student, status='N')
      step_order = 1

    if 'GET' == request.method or 'POST' == request.method:
      steps = models.Step.objects.all().filter(curriculum=instance.assignment.curriculum)
      step = steps.get(order=step_order)
      total_steps = steps.count()
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

      if 'GET' == request.method:
        #get the assignment step
        form = forms.AssignmentStepResponseForm(instance=assignmentStepResponse, prefix="step_response")
        questionResponseFormset=inlineformset_factory(models.AssignmentStepResponse, models.QuestionResponse, form=forms.QuestionResponseForm, can_delete=False, extra=extra)
        formset = questionResponseFormset(instance=assignmentStepResponse, prefix='form')

        if len(initial_data):
          for subform, data in zip(formset.forms, initial_data):
            subform.initial = data

        context = {'form': form, 'formset': formset, 'total_steps': total_steps}
        return render(request, 'ctstem_app/AssignmentStep.html', context)

      elif 'POST' == request.method:
        data = request.POST.copy()
        #is this a save or a submit
        save_only = int(data['save'])
        form = forms.AssignmentStepResponseForm(data, instance=assignmentStepResponse, prefix="step_response")
        questionResponseFormset=inlineformset_factory(models.AssignmentStepResponse, models.QuestionResponse, form=forms.QuestionResponseForm, can_delete=False, extra=0)
        formset = questionResponseFormset(data, request.FILES, instance=assignmentStepResponse, prefix='form')

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

          instance.save()
          #save assignment step response
          assignmentStepResponse = form.save(commit=False)
          assignmentStepResponse.instance = instance
          assignmentStepResponse.save()
          #save the question response formset
          questionResponseObjects = formset.save()
          questionResponses = {}
          # get the question response ids to update the front end
          for questionResponse in questionResponseObjects:
            questionResponses['id_form-%d-id'%(questionResponse.curriculum_question.order-1)] = questionResponse.id

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
              response_data = {'message': 'Your responses were auto saved at %s' % datetime.datetime.now().time().strftime('%r'), 'url': url, 'questionResponses': questionResponses, 'questionCount': len(questionResponses)}
              return http.HttpResponse(json.dumps(response_data), content_type = 'application/json')
            else:
              return shortcuts.redirect('ctstem:resumeAssignment', assignment_id=assignment_id, instance_id=instance.id, step_order=next_step)

        else:
          print form.errors
          print formset.errors
          messages.error(request, 'Please answer all the questions on this step before continuing on to the next step')

        context = {'form': form, 'formset': formset, 'total_steps': total_steps}
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
    if hasattr(request.user, 'teacher') == False and hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to provide feedback</h1>')

    if '' != instance_id:
      instance = models.AssignmentInstance.objects.get(assignment_id=assignment_id, id=instance_id)
      feedback, created = models.AssignmentFeedback.objects.get_or_create(instance=instance)
      stepResponses = models.AssignmentStepResponse.objects.all().filter(instance=instance)
      for stepResponse in stepResponses:
        stepFeeback, created = models.StepFeedback.objects.get_or_create(assignment_feedback=feedback, step_response=stepResponse)

        questionResponses = models.QuestionResponse.objects.all().filter(step_response=stepResponse)
        for questionResponse in questionResponses:
          questionFeedback, created = models.QuestionFeedback.objects.get_or_create(step_feedback=stepFeeback, response=questionResponse)

      if 'GET' == request.method:
        form = forms.FeedbackForm(instance=feedback, prefix='feedback')
        #AssessmentStepFormSet = inlineformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,can_delete=True, can_order=True, extra=1)

        StepFeedbackFormSet = nestedformset_factory(models.AssignmentFeedback, models.StepFeedback, form=forms.StepFeedbackForm,
                                                      nested_formset=inlineformset_factory(models.StepFeedback, models.QuestionFeedback, form=forms.QuestionFeedbackForm, can_delete=False, can_order=False, extra=0),
                                                      can_delete=False, can_order=False, extra=0)


        formset = StepFeedbackFormSet(instance=feedback, prefix='form')

        context = {'form': form, 'formset': formset}
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
            return shortcuts.redirect('ctstem:assignmentDashboard', id=assignment_id)
          else:
            messages.success(request, 'Your feedback has been saved')
        else:
          print form.errors
          print formset.errors
          messages.error(request, 'Your feedback could not be saved')

        context = {'form': form, 'formset': formset}
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
  if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False and hasattr(request.user, 'teacher') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to export student response</h1>')
  try:
    assignment = models.Assignment.objects.get(id=assignment_id)
    response = HttpResponse(content_type='text/csv')
    if '' != student_id:
      student = models.Student.objects.get(id=student_id)
      instances = models.AssignmentInstance.objects.all().filter(assignment=assignment, student=student)
      response['Content-Disposition'] = 'attachment; filename="%s-%s.csv"'% (assignment, student)
    else:
      instances = models.AssignmentInstance.objects.all().filter(assignment=assignment)
      response['Content-Disposition'] = 'attachment; filename="%s.csv"'%assignment


    writer = csv.writer(response)
    writer.writerow(['Group', assignment.group])
    writer.writerow(['Assignment', assignment])
    writer.writerow(['Assigned Date', assignment.assigned_date])
    writer.writerow(['Due Date', assignment.due_date])
    writer.writerow([])
    writer.writerow(['Student', 'Step Title', 'Question', 'Options', 'Response'])
    for instance in instances:
      stepResponses = models.AssignmentStepResponse.objects.all().filter(instance=instance)
      for stepResponse in stepResponses:
        questionResponses = models.QuestionResponse.objects.all().filter(step_response=stepResponse)
        for questionResponse in questionResponses:
          if questionResponse.response:
            response_text = questionResponse.response
          elif questionResponse.responseFile:
            response_text = questionResponse.responseFile.url
          else:
            response_text = ''
          writer.writerow([instance.student, stepResponse.step.title, questionResponse.curriculum_question.question, questionResponse.curriculum_question.question.options, response_text])

    return response

  except models.Assignment.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assignment not found</h1>')
  except models.Student.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested student not found</h1>')


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
    questionForm = forms.QuestionForm(data, instance=question)
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
  teachers = models.Teacher.objects.all().filter(user_code=code)
  researchers = models.Researcher.objects.all().filter(user_code=code)
  schools = models.School.objects.all().filter(school_code=code)
  # ensure the user code is unique across teachers and researchers
  while teachers.count() > 0 or researchers.count() > 0 or schools.count() > 0:
    code = get_random_string(length=5, allowed_chars=allowed_chars)
    teachers = models.Teacher.objects.all().filter(user_code=code)
    researchers = models.Researcher.objects.all().filter(user_code=code)
    schools = models.School.objects.all().filter(school_code=code)

  return code
####################################
# UPLOAD USERS
####################################
@login_required
def user_upload(request):
  if hasattr(request.user, 'administrator'):
    role = 'admin'
  elif hasattr(request.user, 'researcher'):
    role = 'researcher'
  elif hasattr(request.user, 'teacher'):
    role = 'teacher'
  else:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to upload users</h1>')

  count = 0
  added = 0
  current_site = Site.objects.get_current()
  domain = current_site.domain

  if request.method == 'POST':
    form = forms.UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
      f = request.FILES['uploadFile']
      reader = csv.reader(f.read().splitlines(), delimiter=',')
      for row in reader:
        count += 1
        if row[0] != 'Username*':
          username = str(row[0])
          first_name = str(row[1])
          last_name = str(row[2])
          email = str(row[3])
          if role == 'teacher':
            account_type = None
            school_code = None
            permission_code = None;
          else:
            account_type = str(row[4])
            school_code = str(row[5])
            permission_code = str(row[6])
          print username, first_name, last_name, email, account_type, school_code, permission_code
          # check fields are not blank
          if username is None or username == '':
            messages.error(request, 'Username is missing on row %d' % count)
          elif first_name is None or first_name == '':
            messages.error(request, 'First name is missing on row %d' % count)
          elif last_name is None or last_name == '':
            messages.error(request, 'Last name is missing on row %d' % count)
          elif email is None or email == '':
            messages.error(request, 'Email is missing on row %d' % count)
          elif role == 'admin' and account_type not in ['Admin', 'Researcher', 'Teacher', 'Student', 'Author']:
            messages.error(request, 'Account Type is missing or invalid on row %d.  Account type has to be one of %s' % (count, 'Admin, Researcher, Teacher, Student or Author'))
          elif role == 'researcher' and account_type not in ['Teacher', 'Student']:
            messages.error(request, 'Account Type is missing or invalid on row %d.  Account type has to be one of %s' % (count, 'Teacher or Student'))
          elif role == 'teacher' and account_type is not None and account_type != '':
            messages.error(request, 'You do not have the privilege to add  %s on row %d.  Please use a valid Student Template' % (account_type, count))
          # everything cool so far
          else:
            try:

              #generate a random password
              password = User.objects.make_random_password()
              #create the user object
              if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                raise IntegrityError('User already exists')
              user = User.objects.create_user(username=username, email=email, password=password)
              user.first_name = first_name
              user.last_name = last_name
              user.save()
              #check the account type
              #create an admin
              if account_type == 'Admin':
                admin = models.Administrator.objects.create(user=user)
              #create a researcher
              elif account_type == 'Researcher':
                user_code = generate_code_helper(request)
                school_obj = models.School.objects.get(school_code=school_code)
                researcher = models.Researcher.objects.create(user=user, user_code=user_code, school=school_obj)
              #create a teacher
              elif account_type == 'Teacher':
                user_code = generate_code_helper(request)
                school_obj = models.School.objects.get(school_code=school_code)
                teacher = models.Teacher.objects.create(user=user, user_code=user_code, school=school_obj)
                # associate the teacher with a researcher
                if role == 'researcher':
                  #associate the teacher with the login in researcher
                  request.user.researcher.teachers.add(teacher)
                else:
                  #find the researcher with the permission code
                  if permission_code is not None and permission_code != '':
                    researcher = models.Researcher.objects.get(user_code=permission_code)
                    researcher.teachers.add(teacher)
                  else:
                    messages.warning(request, 'Teacher on row %d created but not affiliated with a researcher because permission code not specified' % count)
              #create a student
              elif account_type == 'Student' or (role == 'teacher' and (account_type is None or account_type == '')):
                if role == 'teacher':
                  account_type = 'Student'
                  school_obj = request.user.teacher.school
                  student = models.Student.objects.create(user=user, school=school_obj)
                  #associate student with the logged in teacher
                  request.user.teacher.students.add(student)
                else:
                  #find the teacher with the permission code
                  if permission_code is not None and permission_code != '':
                    teacher = models.Teacher.objects.get(user_code=permission_code)
                    school_obj = teacher.school
                    student = models.Student.objects.create(user=user, school=school_obj)
                    teacher.students.add(student)
                  else:
                    user.delete()
                    messages.warning(request, 'Student on row %d not created because teacher permission code not specified' % count)
                    continue
              #create an author
              else:
                author = models.Author.objects.create(user=user)

              added += 1
              #email user the  user name and password
              send_mail('CT-STEM Account Created',
                    'Your %s account has been created on Computational Thinking in STEM website http://%s.  \r\n\r\n \
                     Please login to the site using the following credentials and change your password.\r\n\r\n  \
                     Username: %s \r\n \
                     Temporary Password: %s \r\n\r\n \
                     -- CT-STEM Admin'%(account_type, domain, user.username, password),
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email])
            except IntegrityError:
              messages.error(request, 'Username and/or email used on row %d already exists, so the user was not created' % count)
              continue
            except models.School.DoesNotExist:
              messages.error(request, 'School %s on row %d does not exist in the system' % (school, count))
              user.delete()
              continue
            except models.Teacher.DoesNotExist:
              messages.error(request, 'Teacher with user code %s on row %d does not exist in the system' % (permission_code, count))
              user.delete()
              continue
            except models.Researcher.DoesNotExist:
              messages.error(request, 'Researcher with user code %s on row %d does not exist in the system' % (permission_code, count))
              user.delete()
              continue
      messages.success(request, '%d out of %d users were added.' % (added, count-1))
      response_data = {'result': 'Success'}
    else:
      print form.errors
      response_data = {'result': 'Failure', 'message': 'The uploaded csv is not valid. Please revise the csv and upload again.'}
    return http.HttpResponse(json.dumps(response_data), content_type="application/json")

  return http.HttpResponseNotAllowed(['POST'])

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
        form.save()
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
  if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False:
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
  if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False:
    return http.HttpResponseNotFound('<h1>You do not have the privilege to edit team roles</h1>')

  members = models.Team.objects.all()
  context = {'members': members}
  return render(request, 'ctstem_app/TeamMembers.html', context)

@login_required
def teamMember(request, id=''):
  try:
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False:
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
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False:
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

