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

####################################
# HOME
####################################
def home(request):
  return render(request, 'ctstem_app/Home.html')

####################################
# PARTNERS
####################################
def partners(request):
  return render(request, 'ctstem_app/Partners.html')
####################################
# ABOUT US
####################################
def about_us(request):
  return render(request, 'ctstem_app/About_us.html')

####################################
# ASSESSMENTS TABLE VIEW
####################################
def assessments(request):
  if hasattr(request.user, 'administrator') == False:
    assessments = models.Assessment.objects.all().filter(status='P').order_by('id')
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
    if hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to modify this assessment</h1>')
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
                                                    nested_formset=inlineformset_factory(models.AssessmentStep, models.AssessmentQuestion, form=forms.AssessmentQuestionForm),
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
        formset.save()
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

  except models.Lesson.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assessment not found</h1>')

####################################
# LESSONS TABLE VIEW
####################################
def lessons(request):
  if hasattr(request.user, 'administrator') == False:
    lessons = models.Lesson.objects.all().filter(status='P').order_by('id')
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
      LessonActivityFormSet = nestedformset_factory(models.Lesson, models.LessonActivity, form=forms.LessonActivityForm,
                                                    nested_formset=inlineformset_factory(models.LessonActivity, models.LessonQuestion, form=forms.LessonQuestionForm, can_delete=True, can_order=True, extra=1),
                                                    can_delete=True, can_order=True, extra=1)
      #QuestionFormSet = inlineformset_factory(models.Lesson, models.LessonQuestion, form=forms.LessonQuestionForm, can_order=True, can_delete=True, extra=1)
      formset = LessonActivityFormSet(instance=lesson, prefix='form')
      context = {'form': form, 'formset':formset, 'newQuestionForm': newQuestionForm}
      return render(request, 'ctstem_app/Lesson.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      form = forms.LessonForm(data, request.FILES, instance=lesson, prefix="lesson")
      LessonActivityFormSet = nestedformset_factory(models.Lesson, models.LessonActivity, form=forms.LessonActivityForm,
                                                    nested_formset=inlineformset_factory(models.LessonActivity, models.LessonQuestion, form=forms.LessonQuestionForm, can_delete=True, can_order=True, extra=1),
                                                    can_delete=True, can_order=True, extra=1)
      #QuestionFormSet = inlineformset_factory(models.Lesson, models.LessonQuestion, form=forms.LessonQuestionForm, can_order=True, can_delete=True, extra=1)
      formset = LessonActivityFormSet(data, instance=lesson, prefix='form')
      print form.is_valid()
      print formset.is_valid()
      if form.is_valid() and formset.is_valid():
        savedLesson = form.save(commit=False)
        if '' == id:
            savedLesson.author = request.user
        savedLesson.modified_by = request.user
        savedLesson.slug = slugify(savedLesson.title) + '-v%s'%savedLesson.version
        savedLesson.save()
        form.save()
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
        messages.error(request, "The lesson could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form, 'formset':formset, 'newQuestionForm': newQuestionForm}
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
          lesson.ngss_standards = original_lesson.ngss_standards.all()
          lesson.ct_stem_practices = original_lesson.ct_stem_practices.all()
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
      form = forms.LessonForm(instance=lesson, prefix='lesson')
      LessonActivityFormSet = nestedformset_factory(models.Lesson, models.LessonActivity, form=forms.LessonActivityForm,
                                                    nested_formset=inlineformset_factory(models.LessonActivity, models.LessonQuestion, form=forms.LessonQuestionForm, can_delete=True, can_order=True, extra=0),
                                                    can_delete=True, can_order=True, extra=0)
      #QuestionFormSet = inlineformset_factory(models.Lesson, models.LessonQuestion, form=forms.LessonQuestionForm, can_order=True, can_delete=True, extra=1)
      formset = LessonActivityFormSet(instance=lesson, prefix='form')
      context = {'form': form, 'formset':formset}

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

def taxonomy(request):
  ngss_standards = models.NGSSStandard.objects.all().order_by('title')
  ctstem_practices_qs = models.CTStemPractice.objects.all().order_by('category', 'order')
  ctstem_practices = {}
  for cp in ctstem_practices_qs:
    if cp.get_category_display() in ctstem_practices:
      ctstem_practices[cp.get_category_display()].append(cp)
    else:
      ctstem_practices[cp.get_category_display()]= [cp]

  context = {'ngss_standards': ngss_standards, 'ctstem_practices': ctstem_practices}
  return render(request, 'ctstem_app/Taxonomy.html', context)

####################################
# NGSS STANDARDS
####################################
@login_required
def ngss_standard(request):
  if hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to view this page</h1>')

  NGSSFormSet = modelformset_factory(models.NGSSStandard, form=forms.NGSSStandardForm, extra=1, can_delete=True)
  if request.method == 'GET':
    formset = NGSSFormSet(queryset=models.NGSSStandard.objects.all())
    context = {'formset': formset}
    return render(request, 'ctstem_app/NGSSStandard.html', context)
  elif request.method == 'POST':
    data = request.POST.copy()
    formset = NGSSFormSet(data)

    if formset.is_valid():
      formset.save()
      messages.success(request, "NGSS Standards saved successfully")
      return shortcuts.redirect('ctstem:ngss_standard')
    else:
      print formset.errors
      context = {'formset': formset}
      return render(request, 'ctstem_app/NGSSStandard.html', context)

  return http.HttpResponseNotAllowed(['GET', 'POST'])

####################################
# NGSS STANDARDS
####################################
@login_required
def ctstem_practice(request):
  if hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to view this page</h1>')

  NGSSFormSet = modelformset_factory(models.CTStemPractice, form=forms.CTStemPracticeForm, extra=1, can_delete=True)
  if request.method == 'GET':
    formset = NGSSFormSet(queryset=models.CTStemPractice.objects.all())
    context = {'formset': formset}
    return render(request, 'ctstem_app/CTStemPractice.html', context)
  elif request.method == 'POST':
    data = request.POST.copy()
    formset = NGSSFormSet(data)

    if formset.is_valid():
      formset.save()
      messages.success(request, "CT-STEM Practices saved successfully")
      return shortcuts.redirect('ctstem:ctstem_practice')
    else:
      print formset.errors
      context = {'formset': formset}
      return render(request, 'ctstem_app/CTStemPractice.html', context)

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

  except models.Lesson.DoesNotExist:
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
  groups = models.UserGroup.objects.all().order_by('id')
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

    print group
    if request.method == 'GET':
        form = forms.UserGroupForm(instance=group, prefix='group')
        context = {'form': form,}
        return render(request, 'ctstem_app/UserGroup.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      form = forms.UserGroupForm(data, instance=group, prefix="group")
      if form.is_valid():
        savedGroup = form.save()
        messages.success(request, "User Group Saved.")
        return shortcuts.redirect('ctstem:group', id=savedGroup.id)
      else:
        print form.errors
        messages.error(request, "The group could not be saved because there were errors.  Please check the errors below.")
        context = {'form': form}
        return render(request, 'ctstem_app/UserGroup.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Lesson.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested group not found</h1>')
####################################
# ADD/EDIT QUESTION
####################################
@login_required
def question(request, id=''):
  # check if the user has permission to add a question
  if hasattr(request.user, 'administrator') == False:
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
  user_code = generate_code_helper(request)
  response_data = {'user_code': user_code}
  return http.HttpResponse(json.dumps(response_data), content_type="application/json")

####################################
# GENERATE UNIQUE USER CODE HELPER
####################################
def generate_code_helper(request):
  allowed_chars = ''.join((string.uppercase, string.digits))
  user_code = get_random_string(length=5, allowed_chars=allowed_chars)
  teachers = models.Teacher.objects.all().filter(user_code=user_code)
  researchers = models.Researcher.objects.all().filter(user_code=user_code)
  # ensure the user code is unique across teachers and researchers
  while teachers.count() > 0 or researchers.count() > 0:
    user_code = get_random_string(length=5, allowed_chars=allowed_chars)
    teachers = models.Teacher.objects.all().filter(user_code=user_code)
    researchers = models.Researcher.objects.all().filter(user_code=user_code)

  return user_code
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
          password = str(row[4])
          account_type = str(row[5])
          school = str(row[6])
          permission_code = str(row[7])
          print username, first_name, last_name, email, password, account_type, school, permission_code
          # check fields are not blank
          if username is None or username == '':
            messages.error(request, 'Username is missing on row %d' % count)
          elif first_name is None or first_name == '':
            messages.error(request, 'First name is missing on row %d' % count)
          elif last_name is None or last_name == '':
            messages.error(request, 'Last name is missing on row %d' % count)
          elif email is None or email == '':
            messages.error(request, 'Email is missing on row %d' % count)
          elif account_type is None or account_type == '' or account_type not in ['Admin', 'Researcher', 'Teacher', 'Student', 'Author']:
            messages.error(request, 'Account Type is missing or invalid on row %d' % count)
          # check user has privilege to create other users
          elif role == 'researcher' and account_type in ['Admin', 'Researcher', 'Author']:
            messages.error(request, 'You do not have the privilege to add  %s on row %d' % (account_type, count))
          elif role == 'teacher' and account_type in ['Admin', 'Researcher', 'Teacher', 'Author']:
            messages.error(request, 'You do not have the privilege to add  %s on row %d' % (account_type, count))
          # everything cool so far
          else:
            try:
              if password is None or password == '':
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
                school_obj = models.School.objects.get(name=school)
                researcher = models.Researcher.objects.create(user=user, user_code=user_code, school=school_obj)
              #create a teacher
              elif account_type == 'Teacher':
                user_code = generate_code_helper(request)
                school_obj = models.School.objects.get(name=school)
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
              elif account_type == 'Student':
                school_obj = models.School.objects.get(name=school)
                student = models.Student.objects.create(user=user, school=school_obj)
                if role == 'teacher':
                  #associate student with the logged in teacher
                  request.user.teacher.students.add(student)
                else:
                  #find the teacher with the permission code
                  if permission_code is not None and permission_code != '':
                    teacher = models.Teacher.objects.get(user_code=permission_code)
                    teacher.students.add(student)
                  else:
                    messages.warning(request, 'Student on row %d created but not affiliated with a teacher because permission code not specified' % count)
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

