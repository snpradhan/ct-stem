from django.http import HttpResponse
from ctstem_app import models, forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django import http, shortcuts, template
from django.shortcuts import render
from django.contrib import auth, messages

# Create your views here.

def index(request):
  lessons = models.Lesson.objects.order_by('id')
  context = {'lessons': lessons}
  return render(request, 'ctstem_app/base.html', context)

def lessons(request):
  lessons = models.Lesson.objects.order_by('id')
  context = {'lessons': lessons}
  return render(request, 'ctstem_app/Lessons.html', context)

def about_us(request):
  return render(request, 'ctstem_app/About_us.html')

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

def user_login(request):
  username = password = ''

  if 'POST' == request.method:
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:
      login(request, user)
      return render(request, 'ctstem_app/About_us.html')
    else:
      messages.error(request, "Your username and/or password were incorrect.")
      return render(request, 'ctstem_app/About_us.html')
  elif 'GET' == request.method:
    lessons = models.Lesson.objects.order_by('id')
    context = {'lessons': lessons}
    return render(request, 'ctstem_app/Lessons.html', context)


@login_required
def user_logout(request):
  logout(request)
  return shortcuts.redirect('ctstem:login')

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
      if role == 'S':
        studentform = forms.StudentForm(instance=student, prefix='student')
        context = {'profileform': studentform, 'userform': userform, }
        return render(request, 'ctstem_app/UserProfile.html', context)

      elif role == 'T':
        teacherform = forms.TeacherForm(instance=teacher, prefix='teacher')
        context = {'profileform': teacherform, 'userform': userform, }
        return render(request, 'ctstem_app/UserProfile.html', context)

      elif role == 'A':
        context = {'userform': userform, }
        return render(request, 'ctstem_app/UserProfile.html', context)

      elif role == 'R':
        researcherform = forms.ResearcherForm(instance=researcher, prefix='researcher')
        context = {'profileform': researcherform, 'userform': userform, }
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
          return shortcuts.redirect('ctstem:lessons')
        elif profileform.is_valid():
          userform.save()
          profileform.save()
          messages.success(request, "User profile saved successfully")
          return shortcuts.redirect('ctstem:lessons')
        else:
          print profileform.errors
          context = {'profileform': profileform, 'userform': userform, }
          return render(request, 'ctstem_app/UserProfile.html', context)
      else:
          print profileform.errors
          print userform.errors
          context = {'profileform': profileform, 'userform': userform, }
          return render(request, 'ctstem_app/UserProfile.html', context)

    return http.HttpResponseNotAllowed(['GET', 'POST'])

  except User.DoesNotExist:
      return http.HttpResponseNotFound('<h1>Requested user not found</h1>')
