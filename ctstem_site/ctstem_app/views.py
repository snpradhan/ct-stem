from django.http import HttpResponse
from ctstem_app import models, forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django import http, shortcuts, template
from django.shortcuts import render
from django.contrib import auth, messages
from django.forms.models import inlineformset_factory, modelformset_factory
from nested_formset import nestedformset_factory
from slugify import slugify
import json

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
      print data
      form = forms.AssessmentForm(data, request.FILES, instance=assessment, prefix="assessment")
      #AssessmentStepFormSet = inlineformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,
                                                    #can_delete=True, can_order=True, extra=0)
      AssessmentStepFormSet = nestedformset_factory(models.Assessment, models.AssessmentStep, form=forms.AssessmentStepForm,
                                                    nested_formset=inlineformset_factory(models.AssessmentStep, models.AssessmentQuestion, form=forms.AssessmentQuestionForm),
                                                    can_delete=True, can_order=True, extra=0)
      formset = AssessmentStepFormSet(data, instance=assessment, prefix='form')
      print form.is_valid()
      print formset.is_valid()
      if form.is_valid() and formset.is_valid():
        savedAssessment = form.save(commit=False)
        if '' == id:
            savedAssessment.author = request.user
        savedAssessment.modified_by = request.user
        savedAssessment.save()
        form.save()
        formset.save()
        messages.success(request, "Assessment Saved.")
        return shortcuts.redirect('ctstem:assessment', id=savedAssessment.id)
      else:
        print form.errors
        print formset.errors
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
                                                    nested_formset=inlineformset_factory(models.AssessmentStep, models.AssessmentQuestion, form=forms.AssessmentQuestionForm, can_delete=True, can_order=True, extra=1),
                                                    can_delete=True, can_order=True, extra=1)
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
      messages.success(request, '%s deleted' % assessment.title)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Lesson.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested assessment not found</h1>')

####################################
# LESSONS TABLE VIEW
####################################
def lessons(request):
  lessons = models.Lesson.objects.order_by('id')
  context = {'lessons': lessons}
  return render(request, 'ctstem_app/Lessons.html', context)

####################################
# CREATE MODIFY A LESSON
####################################
def lesson(request, id=''):
  try:
    # check if the user has permission to create or modify a lesson
    if hasattr(request.user, 'administrator') == False:
      return http.HttpResponseNotFound('<h1>You do not have the privilege to modify this lesson</h1>')
    # check if the lesson exists
    if '' != id:
      lesson = models.Lesson.objects.get(id=id)
    else:
      lesson = models.Lesson()

    newQuestionForm = forms.QuestionForm()

    if request.method == 'GET':
      form = forms.LessonForm(instance=lesson, prefix='lesson')
      QuestionFormSet = inlineformset_factory(models.Lesson, models.LessonQuestion, form=forms.LessonQuestionForm, can_order=True, can_delete=True, extra=1)
      formset = QuestionFormSet(instance=lesson, prefix='question')
      context = {'form': form, 'formset':formset, 'newQuestionForm': newQuestionForm}
      return render(request, 'ctstem_app/Lesson.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      form = forms.LessonForm(data, request.FILES, instance=lesson, prefix="lesson")
      QuestionFormSet = inlineformset_factory(models.Lesson, models.LessonQuestion, form=forms.LessonQuestionForm, can_order=True, can_delete=True, extra=1)
      formset = QuestionFormSet(data, instance=lesson, prefix='question')
      if form.is_valid() and formset.is_valid():
        savedLesson = form.save(commit=False)
        if '' == id:
            savedLesson.author = request.user
        savedLesson.modified_by = request.user
        savedLesson.save()
        form.save()

        #save the questions
        questions = formset.save(commit=False)
        #maintain order
        for qform in formset.ordered_forms:
          qform.instance.order = qform.cleaned_data['ORDER']
          qform.instance.lesson = savedLesson
          qform.instance.save()
        #remove deleted questions
        for obj in formset.deleted_objects:
          obj.delete()

        messages.success(request, "Lesson Saved.")
        return shortcuts.redirect('ctstem:lesson', id=savedLesson.id)
      else:
        print form.errors
        print formset.errors
        context = {'form': form, 'formset':formset, 'newQuestionForm': newQuestionForm}
        return render(request, 'ctstem_app/Lesson.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Lesson.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested lesson not found</h1>')

####################################
# PREVIEW A LESSON
####################################
def previewLesson(request, id=''):
  try:
    # check if the lesson exists
    if '' != id:
      lesson = models.Lesson.objects.get(id=id)
    else:
      lesson = models.Lesson()

    if request.method == 'GET':
      form = forms.LessonForm(instance=lesson, prefix='lesson')
      QuestionFormSet = inlineformset_factory(models.Lesson, models.LessonQuestion, fields=('question', 'order'), extra=1)
      formset = QuestionFormSet(instance=lesson)
      context = {'form': form, 'formset':formset}
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
      messages.success(request, '%s deleted' % lesson.title)
      return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Lesson.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested lesson not found</h1>')
####################################
# REGISTER
####################################
def register(request):
  if request.method == 'POST':
    print request.POST
    form = forms.RegistrationForm(data=request.POST)
    if form.is_valid():
      user = User.objects.create_user(form.cleaned_data['username'],
                                      form.cleaned_data['email'],
                                      form.cleaned_data['password1'])
      user.first_name = form.cleaned_data['first_name']
      user.last_name = form.cleaned_data['last_name']
      if form.cleaned_data['account_type'] in  ['A', 'R']:
          user.is_active = False
      else:
          user.is_active = True
      user.save()

      if form.cleaned_data['account_type'] == 'T':
        newUser = models.Teacher()
        newUser.school = form.cleaned_data['school']
        newUser.permission_code =  form.cleaned_data['user_code']
        newUser.user = user
        newUser.save()
        #get the school admin based on the permission code
        researcher = models.Researcher.objects.get(permission_code = form.cleaned_data['permission_code'])
        researcher.teachers.add(newUser)

      elif form.cleaned_data['account_type'] == 'S':
        newUser = models.Student()
        newUser.school = form.cleaned_data['school']
        newUser.user = user
        newUser.save()
        #get the teacher based on the permission code
        teacher = models.Teacher.objects.get(permission_code = form.cleaned_data['permission_code'])
        teacher.students.add(newUser)

      elif form.cleaned_data['account_type'] == 'A':
          newUser = models.Administrator()
          newUser.user = user
          newUser.save()

      elif form.cleaned_data['account_type'] == 'R':
        newUser = models.Researcher()
        newUser.school = form.cleaned_data['school']
        newUser.permission_code =  form.cleaned_data['user_code']
        newUser.user = user
        newUser.save()

      if form.cleaned_data['account_type'] in ['A', 'R']:
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
     context = {'form': form}
    return render(request, 'ctstem_app/Registration.html', context)

  else:
    form = forms.RegistrationForm()
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
      response_data['result'] = 'failed'
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
      role = 'A'
      admin = models.Administrator.objects.get(user__id=id)
    elif hasattr(user, 'teacher'):
      role = 'T'
      teacher = models.Teacher.objects.get(user__id=id)
    elif hasattr(user, 'student'):
      role = 'S'
      student = models.Student.objects.get(user__id=id)
    elif hasattr(user, 'researcher'):
      role = 'R'
      researcher = models.Researcher.objects.get(user__id=id)
    else:
      return http.HttpResponseForbidden('<h1>User has no role</h1>')

    if request.method == 'GET':
      userform = forms.UserProfileForm(instance=user, prefix='user')
      if role in ['S', 'T', 'A', 'R']:
        if role == 'S':
          profileform = forms.StudentForm(instance=student, prefix='student')
        elif role == 'T':
          profileform = forms.TeacherForm(instance=teacher, prefix='teacher')
        elif role == 'A':
          profileform = None
        elif role == 'R':
          profileform = forms.ResearcherForm(instance=researcher, prefix='researcher')
        else:
          return http.HttpResponseNotFound('<h1>Requested user does not have a role</h1>')

        context = {'profileform': profileform, 'userform': userform, }
        return render(request, 'ctstem_app/UserProfile.html', context)

    elif request.method == 'POST':
      data = request.POST.copy()
      if role == 'S':
          data.__setitem__('student-user', student.user.id)
      elif role == 'T':
          data.__setitem__('teacher-user', teacher.user.id)
      elif role == 'A':
          data.__setitem__('admin-user', admin.user.id)
      elif role == 'R':
          data.__setitem__('researcher-user', researcher.user.id)

      data.__setitem__('user-password', user.password)
      data.__setitem__('user-last_login', user.last_login)
      data.__setitem__('user-date_joined', user.date_joined)
      userform = forms.UserProfileForm(data, instance=user, prefix='user')

      profileform = None
      if role == 'S':
        profileform = forms.StudentForm(data, instance=student, prefix='student')
      elif role == 'T':
        profileform = forms.TeacherForm(data, instance=teacher, prefix='teacher')
      elif role == 'R':
        profileform = forms.ResearcherForm(data, instance=researcher, prefix='researcher')

      if userform.is_valid():
        if profileform is None:
          userform.save()
          messages.success(request, "User profile saved successfully")
          context = {'userform': userform, }
        elif profileform.is_valid():
          userform.save()
          profileform.save()
          messages.success(request, "User profile saved successfully")
          context = {'profileform': profileform, 'userform': userform, }
        else:
          print profileform.errors
          context = {'profileform': profileform, 'userform': userform, }
      else:
        print profileform.errors
        print userform.errors
        context = {'profileform': profileform, 'userform': userform, }

      return render(request, 'ctstem_app/UserProfile.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except User.DoesNotExist:
      return http.HttpResponseNotFound('<h1>Requested user not found</h1>')

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
  if role == 'students':
    users = models.Student.objects.all()
  elif role == 'teachers':
    users = models.Teacher.objects.all()
  elif role == 'admins':
    users = models.Administrator.objects.all()
  elif role == 'researchers':
    users = models.Researcher.objects.all()
  elif role == 'authors':
    users = models.Author.objects.all()
  else:
    users = None
  context = {'users': users, 'role': role}
  return render(request, 'ctstem_app/Users.html', context)

####################################
# PUBLICATIONS TABLE VIEW
####################################
def publications(request):
  if hasattr(request.user, 'administrator') == False:
    publications = models.Publication.objects.filter(viewable=True).order_by('created')
  else:
    publications = models.Publication.objects.order_by('created')
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
        context = {'form': form}
        return render(request, 'ctstem_app/Publication.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except models.Lesson.DoesNotExist:
    return http.HttpResponseNotFound('<h1>Requested publication not found</h1>')

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




