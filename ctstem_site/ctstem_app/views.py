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

####################################
# HOME
####################################
def home(request):
  return render(request, 'ctstem_app/Home.html')

####################################
# ABOUT US
####################################
def team(request):
  roles = models.TeamRole.objects.all()
  context = {'roles': roles}
  return render(request, 'ctstem_app/Team.html', context)

####################################
# ASSESSMENTS TABLE VIEW
####################################
def assessments(request):
  if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False:
    if request.user.is_authenticated():
      assessments = models.Assessment.objects.all().filter(Q(status='P') | Q(author=request.user)).order_by('id')
    else:
      assessments = models.Assessment.objects.all().filter(Q(status='P')).order_by('id')
  else:
    assessments = models.Assessment.objects.order_by('id')
  context = {'assessments': assessments}
  return render(request, 'ctstem_app/Assessments.html', context)


####################################
# CREATE MODIFY AN ASSESSMENT
####################################
def assessment(request, id=''):
  try:
    # check if the user has permission to create or modify a lesson
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False and hasattr(request.user, 'author') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to create/modify assessments</h1>')
    # check if the lesson exists
    if '' != id:
      assessment = models.Assessment.objects.get(id=id)
    else:
      assessment = models.Assessment()

    if request.method == 'GET':
      form = forms.AssessmentForm(instance=assessment, prefix='assessment')
      #AssessmentStepFormSet = inlineformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,can_delete=True, can_order=True, extra=1)

      AssessmentStepFormSet = nestedformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,
                                                    nested_formset=inlineformset_factory(models.AssessmentStep, models.AssessmentQuestion, form=forms.AssessmentQuestionForm, can_delete=True, can_order=True, extra=1),
                                                    can_delete=True, can_order=True, extra=1)
      formset = AssessmentStepFormSet(instance=assessment, prefix='form')
      context = {'form': form, 'formset':formset}
      return render(request, 'ctstem_app/Assessment.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      form = forms.AssessmentForm(data, request.FILES, instance=assessment, prefix="assessment")
      #AssessmentStepFormSet = inlineformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,
                                                    #can_delete=True, can_order=True, extra=0)
      AssessmentStepFormSet = nestedformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,
                                                    nested_formset=inlineformset_factory(models.AssessmentStep, models.AssessmentQuestion, form=forms.AssessmentQuestionForm, can_delete=True, can_order=True, extra=1),
                                                    can_delete=True, can_order=True, extra=1)
      formset = AssessmentStepFormSet(data, instance=assessment, prefix='form')
      print form.is_valid()
      print formset.is_valid()
      if form.is_valid() and formset.is_valid():
        savedAssessment = form.save(commit=False)
        if '' == id:
            savedAssessment.author = request.user
        savedAssessment.modified_by = request.user
        savedAssessment.slug = slugify(savedAssessment.title) + '-v%s'%savedAssessment.version
        savedAssessment.save()
        form.save()
        formset.save(commit=False)
        for stepform in formset.ordered_forms:
          stepform.instance.order = stepform.cleaned_data['ORDER']
          stepform.instance.lesson = savedAssessment
          stepform.instance.save()
          for qform in stepform.nested.ordered_forms:
            qform.instance.order = qform.cleaned_data['ORDER']
            qform.instance.assessment_step = stepform.instance
            qform.instance.save()
          for obj in stepform.nested.deleted_objects:
            obj.delete()
        #remove deleted questions
        for obj in formset.deleted_objects:
          obj.delete()

        messages.success(request, "Assessment Saved.")
        return shortcuts.redirect('ctstem:assessment', id=savedAssessment.id)
      else:
        print form.errors
        print formset.errors
        messages.error(request, "The assessment could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form, 'formset':formset}
        return render(request, 'ctstem_app/Assessment.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Assessment.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assessment not found</h1>')

####################################
# PREVIEW A LESSON
####################################
def previewAssessment(request, id=''):
  try:
    # check if the lesson exists
    if '' != id:
      assessment = models.Assessment.objects.get(id=id)
    else:
      assessment = models.Assessment()

    if request.method == 'GET':
      form = forms.AssessmentForm(instance=assessment, prefix='assessment')
      #AssessmentStepFormSet = inlineformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,can_delete=True, can_order=True, extra=1)

      AssessmentStepFormSet = nestedformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,
                                                    nested_formset=inlineformset_factory(models.AssessmentStep, models.AssessmentQuestion, form=forms.AssessmentQuestionForm, can_delete=True, can_order=True, extra=0),
                                                    can_delete=True, can_order=True, extra=0)
      formset = AssessmentStepFormSet(instance=assessment, prefix='form')
      context = {'form': form, 'formset':formset}
      return render(request, 'ctstem_app/AssessmentPreview.html', context)

    return http.HttpResponseNotAllowed(['GET'])

  except models.Lesson.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested lesson not found</h1>')

####################################
# DELETE AN ASSESSMENT
####################################
def deleteAssessment(request, id=''):
  try:
    # check if the user has permission to delete a lesson
    if hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to delete this assessment</h1>')
    # check if the lesson exists
    if '' != id:
      assessment = models.Assessment.objects.get(id=id)
    else:
      raise models.Assessment.DoesNotExist

    if request.method == 'GET' or request.method == 'POST':
      assessment.delete()
      messages.success(request, 'Assessment %s deleted' % assessment.title)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Assessment.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assessment not found</h1>')

####################################
# DELETE AN ASSESSMENT
####################################
def assessmentMeta(request, id=''):
  try:
    if '' != id:
      assessment = models.Assessment.objects.get(id=id)
      if 'GET' == request.method:
        context = {'assessment': assessment}
        return render(request, 'ctstem_app/AssessmentMeta.html', context)
      return http.HttpResponseNotAllowed(['GET'])
    else:
      raise models.Assessment.DoesNotExist
  except models.Assessment.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assessment not found</h1>')

####################################
# LESSONS TABLE VIEW
####################################
def lessons(request):
  if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False:
    if request.user.is_authenticated():
      lessons = models.Lesson.objects.all().filter(Q(status='P') | Q(author=request.user)).order_by('id')
    else:
      lessons = models.Lesson.objects.all().filter(Q(status='P')).order_by('id')
  else:
    lessons = models.Lesson.objects.order_by('id')
  context = {'lessons': lessons}
  return render(request, 'ctstem_app/Lessons.html', context)

####################################
# CREATE MODIFY A LESSON
####################################
def lesson(request, id=''):
  try:
    # check if the user has permission to create or modify a lesson
    if hasattr(request.user, 'administrator') == False and hasattr(request.user, 'researcher') == False and hasattr(request.user, 'author') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to modify this lesson</h1>')
    # check if the lesson exists
    if '' != id:
      lesson = models.Lesson.objects.get(id=id)
    else:
      lesson = models.Lesson()

    newQuestionForm = forms.QuestionForm()

    if request.method == 'GET':
      form = forms.LessonForm(instance=lesson, prefix='lesson')
      AttachmentFormSet = inlineformset_factory(models.Lesson, models.Attachment, form=forms.AttachmentForm, can_delete=True, extra=1)
      LessonActivityFormSet = nestedformset_factory(models.Lesson, models.LessonActivity, form=forms.LessonActivityForm,
                                                    nested_formset=inlineformset_factory(models.LessonActivity, models.LessonQuestion, form=forms.LessonQuestionForm, can_delete=True, can_order=True, extra=1),
                                                    can_delete=True, can_order=True, extra=1)
      #QuestionFormSet = inlineformset_factory(models.Lesson, models.LessonQuestion, form=forms.LessonQuestionForm, can_order=True, can_delete=True, extra=1)
      formset = LessonActivityFormSet(instance=lesson, prefix='form')
      attachment_formset = AttachmentFormSet(instance=lesson, prefix='attachment_form')
      context = {'form': form, 'attachment_formset': attachment_formset, 'formset':formset, 'newQuestionForm': newQuestionForm}
      return render(request, 'ctstem_app/Lesson.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      print request.FILES
      form = forms.LessonForm(data, request.FILES, instance=lesson, prefix="lesson")
      AttachmentFormSet = inlineformset_factory(models.Lesson, models.Attachment, form=forms.AttachmentForm, can_delete=True, extra=1)
      LessonActivityFormSet = nestedformset_factory(models.Lesson, models.LessonActivity, form=forms.LessonActivityForm,
                                                    nested_formset=inlineformset_factory(models.LessonActivity, models.LessonQuestion, form=forms.LessonQuestionForm, can_delete=True, can_order=True, extra=1),
                                                    can_delete=True, can_order=True, extra=1)
      #QuestionFormSet = inlineformset_factory(models.Lesson, models.LessonQuestion, form=forms.LessonQuestionForm, can_order=True, can_delete=True, extra=1)
      formset = LessonActivityFormSet(data, instance=lesson, prefix='form')
      attachment_formset = AttachmentFormSet(data, request.FILES, instance=lesson, prefix='attachment_form')
      print 'form ', form.is_valid()
      print 'formset ', formset.is_valid()
      print 'attachment ', attachment_formset.is_valid()

      if form.is_valid() and formset.is_valid() and attachment_formset.is_valid():
        savedLesson = form.save(commit=False)
        if '' == id:
            savedLesson.author = request.user
        savedLesson.modified_by = request.user
        savedLesson.slug = slugify(savedLesson.title) + '-v%s'%savedLesson.version
        savedLesson.save()
        form.save()
        attachment_formset.save()
        formset.save(commit=False)
        for aform in formset.ordered_forms:
          aform.instance.order = aform.cleaned_data['ORDER']
          aform.instance.lesson = savedLesson
          aform.instance.save()
          for qform in aform.nested.ordered_forms:
            qform.instance.order = qform.cleaned_data['ORDER']
            qform.instance.lesson_activity = aform.instance
            qform.instance.save()
          for obj in aform.nested.deleted_objects:
            obj.delete()
        #remove deleted questions
        for obj in formset.deleted_objects:
          obj.delete()

        #save the questions
        '''questions = formset.save(commit=False)
        #maintain order
        for qform in formset.ordered_forms:
          qform.instance.order = qform.cleaned_data['ORDER']
          qform.instance.lesson = savedLesson
          qform.instance.save()
        #remove deleted questions
        for obj in formset.deleted_objects:
          obj.delete()'''

        messages.success(request, "Lesson %s Saved."%savedLesson.title)
        return shortcuts.redirect('ctstem:lesson', id=savedLesson.id)
      else:
        print form.errors
        print formset.errors
        print attachment_formset.errors
        messages.error(request, "The lesson could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form, 'attachment_formset': attachment_formset, 'formset':formset, 'newQuestionForm': newQuestionForm}
        return render(request, 'ctstem_app/Lesson.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Lesson.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested lesson not found</h1>')

####################################
# Lesson Copy
####################################
def copyLesson(request, id=''):
  try:
    # check if the user has permission to create or modify a lesson
    if hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to modify this lesson</h1>')
    # check if the lesson exists
    else:
      if request.method == 'GET' or request.method == 'POST':
        if '' != id:
          lesson = models.Lesson.objects.get(id=id)
          lessonActivities = models.LessonActivity.objects.all().filter(lesson=lesson)
          title = lesson.title
          lesson.title = str(datetime.datetime.now())
          lesson.slug = slugify(lesson.title)
          lesson.pk = None
          lesson.id = None
          lesson.save()

          original_lesson = models.Lesson.objects.get(id=id)
          lesson.title = title
          lesson.author = request.user
          lesson.modified_by = request.user
          lesson.created_date = datetime.datetime.now()
          lesson.modified_date = datetime.datetime.now()
          lesson.parent = original_lesson
          lesson.status = 'D'
          lesson.version = int(original_lesson.version) + 1
          lesson.slug = slugify(lesson.title) + '-v%s'%lesson.version + '-%s'%lesson.id
          lesson.subject = original_lesson.subject.all()
          lesson.taxonomy = original_lesson.taxonomy.all()
          lesson.save()

          for activity in lessonActivities:
              activity_questions = models.LessonQuestion.objects.all().filter(lesson_activity=activity)
              activity.pk = None
              activity.id = None
              activity.lesson = lesson
              activity.save()
              for activity_question in activity_questions:
                  question = activity_question.question
                  question.id = None
                  question.pk = None
                  question.save()

                  activity_question.id = None
                  activity_question.pk = None
                  activity_question.question = question
                  activity_question.lesson_activity = activity
                  activity_question.save()

          messages.success(request, "A new copy of %s created.  Please archive the original lesson" % original_lesson.title)
          return shortcuts.redirect('ctstem:lessons')
      return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Lesson.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested lesson not found</h1>')

####################################
# Lesson PDF
####################################
def previewLesson(request, id='', pdf='0'):
  try:
    # check if the lesson exists
    if '' != id:
      lesson = models.Lesson.objects.get(id=id)
    else:
      lesson = models.Lesson()

    if request.method == 'GET':
      activities = models.LessonActivity.objects.all().filter(lesson=lesson)
      attachments = models.Attachment.objects.all().filter(lesson=lesson)

      context = {'lesson': lesson, 'attachments': attachments, 'activities':activities}
      #print settings.STATIC_ROOT
      if pdf == '1':
        return render_to_pdf_response('ctstem_app/LessonPreview.html', context, u'%s.%s'%(lesson.slug, 'pdf') )
      else:
        return render(request, 'ctstem_app/LessonPreview.html', context)

    return http.HttpResponseNotAllowed(['GET'])

  except models.Lesson.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested lesson not found</h1>')

####################################
# DELETE A LESSON
####################################
def deleteLesson(request, id=''):
  try:
    # check if the user has permission to delete a lesson
    if hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to delete this lesson</h1>')
    # check if the lesson exists
    if '' != id:
      lesson = models.Lesson.objects.get(id=id)
    else:
      raise models.Lesson.DoesNotExist

    if request.method == 'GET' or request.method == 'POST':
      lesson.delete()
      messages.success(request, 'Lesson %s deleted' % lesson.title)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Lesson.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested lesson not found</h1>')
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

      if request.user.is_anonymous():
        if form.cleaned_data['account_type'] in ['A', 'R', 'C']:
          messages.info(request, 'Your account is pending admin approval.  Please contact the system administrator to request approval.')
          return render(request, 'ctstem_app/About_us.html')
        elif form.cleaned_data['account_type'] in ['T', 'S']:
          new_user = authenticate(username=form.cleaned_data['username'],
                                  password=form.cleaned_data['password1'], )
          login(request, new_user)
          lessons = models.Lesson.objects.order_by('id')
          context = {'lessons': lessons}
          return render(request, 'ctstem_app/Lessons.html', context)
      else:
        messages.info(request, 'User account has been created.')
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
    else:
      response_data['result'] = 'Failed'
      if user and user.is_active == False:
        response_data['message'] = 'Your account has not been activated'
      else:
        response_data['message'] = 'Your username and/or password is invalid'
    return http.HttpResponse(json.dumps(response_data), content_type="application/json")

  elif 'GET' == request.method:
    lessons = models.Lesson.objects.order_by('id')
    context = {'lessons': lessons}
    return render(request, 'ctstem_app/Lessons.html', context)

####################################
# USER LOGOUT
####################################
@login_required
def user_logout(request):
  logout(request)
  return shortcuts.redirect('ctstem:login')

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
          context = {'userform': userform, }
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
      #QuestionFormSet = inlineformset_factory(models.Lesson, models.LessonQuestion, form=forms.LessonQuestionForm, can_order=True, can_delete=True, extra=1)
      #CategoryFormSet = inlineformset_factory(models.Standard, models.Category, form=forms.CategoryForm, can_delete=True, extra=1)
      #QuestionFormSet = inlineformset_factory(models.Lesson, models.LessonQuestion, form=forms.LessonQuestionForm, can_order=True, can_delete=True, extra=1)
      formset = CategoryFormSet(instance=standard, prefix='form')
      context = {'form': form, 'formset':formset}
      return render(request, 'ctstem_app/Standard.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      form = forms.StandardForm(data, instance=standard, prefix='standard')
      CategoryFormSet = nestedformset_factory(models.Standard, models.Category, form=forms.CategoryForm,
                                                    nested_formset=inlineformset_factory(models.Category, models.Subcategory, form=forms.SubcategoryForm, can_delete=True, can_order=True, extra=1),
                                                    can_delete=True, can_order=True, extra=1)
      #CategoryFormSet = inlineformset_factory(models.Standard, models.Category, form=forms.CategoryForm, can_delete=True, extra=1)
      formset = CategoryFormSet(data, instance=standard, prefix='form')
      print form.is_valid()
      print formset.is_valid()
      if form.is_valid() and formset.is_valid():
        savedStandard = form.save()
        formset.save()
        messages.success(request, "Standard Saved.")
        return shortcuts.redirect('ctstem:standard', id=savedStandard.id)
      else:
        print form.errors
        print formset.errors
        messages.error(request, "The standard could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form, 'formset':formset}
        return render(request, 'ctstem_app/Standard.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Lesson.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested group not found</h1>')

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
  context = {'groups': groups}
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
        context = {'form': form, 'formset': formset}
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
        context = {'form': form, 'formset':formset}
        return render(request, 'ctstem_app/UserGroup.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Lesson.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested group not found</h1>')

####################################
# STUDENT ASSIGNMENTS
####################################
@login_required
def assignments(request):
  try:
    if hasattr(request.user, 'student') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to view assignments</h1>')

    student = request.user.student
    if request.method == 'GET':
      groups = models.Membership.objects.all().filter(student=student).values_list('group', flat=True)
      print groups
      #for each group
      assignments = models.Assignment.objects.all().filter(group__in=groups)
      assignment_list = []
      for assignment in assignments:
        try:
          instance = models.AssignmentInstance.objects.get(assignment=assignment, student=student)
        except models.AssignmentInstance.DoesNotExist:
          instance = None

        assignment_list.append({'assignment': assignment, 'instance': instance})
      context = {'assignment_list': assignment_list}
      return render(request, 'ctstem_app/Assignments.html', context)
    return http.HttpResponseNotAllowed(['GET'])

  except models.Student.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested student not found</h1>')

####################################
# STUDENT ATTEMPTING ASSIGNMENTS
####################################
@login_required
def assignment(request, assignment_id='', instance_id='', step_order=''):
  try:
    if hasattr(request.user, 'student') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to do this assignments</h1>')

    if '' != instance_id:
      instance = models.AssignmentInstance.objects.get(id=instance_id)
    else:
      instance = models.AssignmentInstance(assignment_id=assignment_id, student=request.user.student, status='N')
      step_order = 1

    if 'GET' == request.method or 'POST' == request.method:
      assessmentSteps = models.AssessmentStep.objects.all().filter(assessment=instance.assignment.assessment)
      assessmentStep = assessmentSteps.get(order=step_order)
      total_steps = assessmentSteps.count()
      initial_data = []
      try:
        assignmentStepResponse = models.AssignmentStepResponse.objects.get(instance=instance, assessment_step=assessmentStep)
        extra = 0
      except models.AssignmentStepResponse.DoesNotExist:
        #unsaved object
        assignmentStepResponse = models.AssignmentStepResponse(instance=instance, assessment_step=assessmentStep)
        assessmentQuestions = models.AssessmentQuestion.objects.all().filter(assessment_step=assessmentStep).order_by('order')
        extra = assessmentQuestions.count()
        for assessmentQuestion in assessmentQuestions:
          initial_data.append({'assessment_question': assessmentQuestion.id, 'response': ''})


      if 'GET' == request.method:
        #get the assignment step
        form = forms.AssignmentStepResponseForm(instance=assignmentStepResponse, prefix="step_response")
        questionResponseFormset=inlineformset_factory(models.AssignmentStepResponse, models.QuestionResponse, form=forms.QuestionResponseForm, can_delete=False, extra=extra)
        formset = questionResponseFormset(instance=assignmentStepResponse, prefix='form')

        if len(initial_data):
          for subform, data in zip(formset.forms, initial_data):
            subform.initial = data

        #context = {'step': assessmentStep, 'instance': instance, 'total_steps': total_steps}
        context = {'form': form, 'formset': formset, 'total_steps': total_steps}
        return render(request, 'ctstem_app/AssignmentStep.html', context)
      elif 'POST' == request.method:
        data = request.POST.copy()

        form = forms.AssignmentStepResponseForm(data, instance=assignmentStepResponse, prefix="step_response")
        questionResponseFormset=inlineformset_factory(models.AssignmentStepResponse, models.QuestionResponse, form=forms.QuestionResponseForm, can_delete=False, extra=0)
        formset = questionResponseFormset(data, instance=assignmentStepResponse, prefix='form')

        if form.is_valid() and formset.is_valid():
          instance.last_step = assessmentStep.order
          if assessmentStep.order < total_steps:
            instance.status = 'P'
          else:
            instance.status = 'S'
          instance.save()
          assignmentStepResponse = form.save(commit=False)
          assignmentStepResponse.instance = instance
          assignmentStepResponse.save()
          formset.save()
          #update the instance
          if instance.status == 'P':
            return shortcuts.redirect('ctstem:resumeAssignment', assignment_id=assignment_id, instance_id=instance.id, step_order=assessmentStep.order+1)
          else:
            messages.success(request, 'Your assignment has been submitted')
            return shortcuts.redirect('ctstem:assignments')
        else:
          print form.errors
          print formset.errors
          messages.error(request, 'Please check the errors below')

        context = {'form': form, 'formset': formset, 'total_steps': total_steps}
        return render(request, 'ctstem_app/AssignmentStep.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])
  except models.AssignmentInstance.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assignment not found</h1>')
  except models.AssessmentStep.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Assessment Step not found </h1>')


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
              #create an author
              else:
                author = models.Author.objects.create(user=user)

              added += 1

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

  TeamRoleFormSet = modelformset_factory(models.TeamRole, form=forms.TeamRoleForm)
  if request.method == 'GET':
    formset = TeamRoleFormSet(queryset=models.TeamRole.objects.all())
    context = {'formset': formset}
    return render(request, 'ctstem_app/TeamRoles.html', context)
  elif request.method == 'POST':
    data = request.POST.copy()
    formset = TeamRoleFormSet(data, queryset=models.TeamRole.objects.all())
    if formset.is_valid():
      formset.save()
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


