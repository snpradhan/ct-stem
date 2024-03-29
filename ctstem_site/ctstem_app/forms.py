from django import forms
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from ctstem_app import models, widgets, util
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory
from datetime import datetime, date
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.widgets import RadioSelect, FileInput, ClearableFileInput
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from tinymce.widgets import TinyMCE
from django.db.models import Q
from django.db.models.functions import Lower
from PIL import Image
import io
import os
from dal import autocomplete
import ast


####################################
# Login Form
####################################
class LoginForm (forms.Form):
  username_email = forms.CharField(required=True, max_length=75, label='Username or Email',
                              error_messages={'required': 'Username or email is required'})
  password = forms.CharField(required=True, widget=forms.PasswordInput(render_value=False), label='Password',
                              error_messages={'required': 'Password is required'})

  def __init__(self, *args, **kwargs):
    super(LoginForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text


  def clean_username_email(self):
    return self.cleaned_data['username_email'].strip()

  def clean(self):
    cleaned_data = super(LoginForm, self).clean()
    username_email = cleaned_data.get('username_email')
    password = cleaned_data.get('password')

    if username_email is None:
      self.fields['username_email'].widget.attrs['class'] += ' error'
    if password is None:
      self.fields['password'].widget.attrs['class'] += ' error'

    if username_email is not None:
      if User.objects.filter(username=username_email.lower()).count() == 0 and User.objects.filter(email=username_email.lower()).count() == 0:
        self.add_error('username_email', 'Username or email is incorrect.')
        self.fields['username_email'].widget.attrs['class'] += ' error'
      elif password is not None:
        username = None
        if User.objects.filter(username=username_email.lower()).count() == 1:
          username = username_email.lower()
        elif User.objects.filter(email=username_email.lower()).count() == 1:
          username = User.objects.get(email=username_email.lower()).username.lower()

        user = authenticate(username=username, password=password)
        if user is None:
          self.add_error('password', 'Password is incorrect.')
          self.fields['password'].widget.attrs['class'] += ' error'

####################################
# Registration Form
####################################
class RegistrationForm (forms.Form):
  email = forms.EmailField(required=True, max_length=75, label='Email')
  confirm_email = forms.EmailField(required=True, max_length=75, label='Confirm Email')
  username = forms.RegexField(required=True, regex=r'^\w+$', max_length=30, label='Username',
                              error_messages={'invalid': 'Usernames may only contain letters, numbers, and underscores (_)'})
  first_name = forms.CharField(required=True, max_length=30, label='First name')
  last_name = forms.CharField(required=True, max_length=30, label='Last name')
  password1 = forms.CharField(required=True, widget=forms.PasswordInput(render_value=False), label='Password')
  password2 = forms.CharField(required=True, widget=forms.PasswordInput(render_value=False), label='Confirm Password')
  account_type = forms.ChoiceField(required=True, choices = models.USER_ROLE_CHOICES)
  school = forms.ModelChoiceField(required=False,
                                  queryset=models.School.objects.all().filter(is_active=True).order_by('name'),
                                  widget=autocomplete.ModelSelect2(url='school-autocomplete',
                                                                   attrs={'data-placeholder': 'Start typing the school name ...',}),
                                  )
  test_account = forms.BooleanField(required=False)

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    group_id = None
    if 'group_id' in kwargs:
      group_id = kwargs.pop('group_id')
    super(RegistrationForm, self).__init__(*args, **kwargs)
    if user.is_authenticated:
      self.fields.pop('confirm_email')
      if hasattr(user, 'researcher'):
        self.fields['account_type'].choices = models.USER_ROLE_CHOICES[3:5]
      elif hasattr(user, 'school_administrator'):
        self.fields['account_type'].choices = models.USER_ROLE_CHOICES[4:]
        self.fields['school'].queryset = models.School.objects.filter(id=user.school_administrator.school.id)
      elif hasattr(user, 'teacher'):
        self.fields['account_type'].choices = models.USER_ROLE_CHOICES[5:]
        self.fields['school'].queryset = models.School.objects.filter(id=user.teacher.school.id)

    elif group_id:
      self.fields.pop('confirm_email')
      self.fields.pop('test_account')
      self.fields['account_type'].choices = models.USER_ROLE_CHOICES[3:]
      if kwargs.get('initial', None) and kwargs['initial']['email']:
        self.fields['email'].widget.attrs['readonly'] = True
    else:
      self.fields.pop('test_account')
      self.fields['account_type'].choices = models.USER_ROLE_CHOICES[4:5]

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text
      if field_name != 'school':
        field.error_messages['required'] = '{fieldname} is required'.format(fieldname=field.label)


  def clean_username(self):
    return self.cleaned_data['username'].strip()

  def clean_email(self):
    return self.cleaned_data['email'].strip()

  def clean_confirm_email(self):
    return self.cleaned_data['confirm_email'].strip()

  def clean(self):
    cleaned_data = super(RegistrationForm, self).clean()
    username = cleaned_data.get('username')
    first_name = cleaned_data.get('first_name')
    last_name = cleaned_data.get('last_name')
    password1 = cleaned_data.get('password1')
    password2 = cleaned_data.get('password2')
    email = cleaned_data.get('email')
    confirm_email = cleaned_data.get('confirm_email')
    account_type = cleaned_data.get('account_type')
    school = cleaned_data.get('school')

    if username is None:
      self.fields['username'].widget.attrs['class'] += ' error'
    elif User.objects.filter(username=username.lower()).count() > 0:
      self.add_error('username', 'This username is already taken. Please choose another.')
      self.fields['username'].widget.attrs['class'] += ' error'

    if password1 is None:
      self.fields['password1'].widget.attrs['class'] += ' error'
    if password2 is None:
      self.fields['password2'].widget.attrs['class'] += ' error'
    if password1 != password2:
      self.add_error('password1', 'Passwords do not match.')
      self.fields['password1'].widget.attrs['class'] += ' error'
      self.fields['password2'].widget.attrs['class'] += ' error'

    if first_name is None:
      self.fields['first_name'].widget.attrs['class'] += ' error'
    if last_name is None:
      self.fields['last_name'].widget.attrs['class'] += ' error'
    if email is None:
      self.fields['email'].widget.attrs['class'] += ' error'
    elif User.objects.filter(email=email).count() > 0:
      self.add_error('email', 'This email is already taken. Please choose another.')
      self.fields['email'].widget.attrs['class'] += ' error'
    elif 'confirm_email' in self.fields and email != confirm_email:
      self.add_error('confirm_email', 'Emails do not match.')
      self.fields['email'].widget.attrs['class'] += ' error'
      self.fields['confirm_email'].widget.attrs['class'] += ' error'
    #check fields for Teacher, Student and School Administrator
    if account_type in ['T', 'S', 'P'] and school is None:
      self.fields['school'].widget.attrs['class'] += ' error'
      self.add_error('school', 'School is required.')



class PreRegistrationForm(forms.Form):
  email = forms.EmailField(required=True, max_length=75, label='Email')

  def __init__(self, *args, **kwargs):
    super(PreRegistrationForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text

  def is_valid(self, group_id):
    valid = super(PreRegistrationForm, self).is_valid()
    if not valid:
      return valid

    email = self.cleaned_data['email']

    try:
      group = models.UserGroup.objects.get(id=group_id)
      user = User.objects.get(email=email)
      student = models.Student.objects.get(user=user)
      if group.teacher.school != student.school:
        self.errors['email'] = 'Your student account belongs to a different school and you cannot join this class.'
        return False
    except User.MultipleObjectsReturned:
      self.errors['email'] = 'More than one account exists for this email. Contact your system admin.'
      return False
    except User.DoesNotExist:
      return True
    except models.Student.DoesNotExist:
      self.errors['email'] = 'Email exists in the system but is not associated with a student account'
      return False

    return True

####################################
# Validation Form
####################################
class ValidationForm (forms.Form):
  username = forms.RegexField(required=True, regex=r'^\w+$', max_length=30, label='Username', help_text="Enter your username")
  password = forms.CharField(required=True, widget=forms.PasswordInput(render_value=False), label='Password', help_text="Enter your password")
  validation_code = forms.CharField(required=True, label='Validation Code', help_text="Enter the validation code")

  def __init__(self, *args, **kwargs):
    super(ValidationForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text
      field.error_messages['required'] = '{fieldname} is required'.format(fieldname=field.label)


  def clean(self):
    cleaned_data = super(ValidationForm, self).clean()
    username = cleaned_data.get('username')
    password = cleaned_data.get('password')
    validation_code = cleaned_data.get('validation_code')

    user = teacher = None
    if username is None:
      self.fields['username'].widget.attrs['class'] += ' error'
    else:
      try:
        user = User.objects.get(username=username)
        teacher = models.Teacher.objects.get(user=user)
      except (User.DoesNotExist, models.Teacher.DoesNotExist):
        self.add_error('username', 'Username is incorrect.')
        self.fields['username'].widget.attrs['class'] += ' error'

    if password is None:
      self.fields['password'].widget.attrs['class'] += ' error'
    elif teacher and not user.check_password(password):
      self.add_error('password', 'Password is incorrect.')
      self.fields['password'].widget.attrs['class'] += ' error'

    if validation_code is None:
      self.fields['validation_code'].widget.attrs['class'] += ' error'
    elif teacher and teacher.validation_code != validation_code:
      self.add_error('validation_code', 'Validation Code is incorrect.')
      self.fields['validation_code'].widget.attrs['class'] += ' error'


####################################
# UserProfile Form
####################################
class UserProfileForm(ModelForm):
  password1 = forms.CharField(widget=forms.PasswordInput, required=False, label='Password', help_text="Leave this field blank to retain old password")
  password2 = forms.CharField(widget=forms.PasswordInput, required=False, label='Confirm Password')

  class Meta:
    model = models.User
    fields = ["username","first_name", "last_name", "email", "password1", "password2", "is_active"]

  def __init__(self, *args, **kwargs):
    super(UserProfileForm, self).__init__(*args, **kwargs)
    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text

  def clean_username(self):
    return self.cleaned_data['username'].strip()

  def clean_email(self):
    return self.cleaned_data['email'].strip()

  def save(self, commit=True):
    if self.cleaned_data['password1'] is not None and self.cleaned_data['password1'] != "":
      user = super(UserProfileForm, self).save(commit=True)
      user.set_password(self.cleaned_data['password1'])
      user.save()
      return user
    else:
      user = super(UserProfileForm, self).save(commit=True)
      user.save()
      return user

  def is_valid(self, user_id):
    valid = super(UserProfileForm, self).is_valid()
    if not valid:
      return valid

    cleaned_data = super(UserProfileForm, self).clean()
    username = cleaned_data.get('username')
    first_name = cleaned_data.get('first_name')
    last_name = cleaned_data.get('last_name')
    password1 = cleaned_data.get('password1')
    password2 = cleaned_data.get('password2')
    email = cleaned_data.get('email')

    if username is None or username == '':
      self.add_error('username', 'Username is required')
      valid = False
    elif User.objects.filter(username=username.lower()).exclude(id=user_id).count() > 0:
      self.add_error('username', 'This username is already taken. Please choose another.')
      valid = False

    if password1 != password2:
      self.add_error('password1', 'Passwords do not match.')
      valid = False

    if first_name is None or first_name == '':
      self.add_error('first_name', 'First name is required')
      valid = False
    if last_name is None or last_name == '':
      self.add_error('last_name', 'Last name is required')
      valid = False
    if email is None or email == '':
      self.add_error('email', 'Email is required')
      valid = False
    elif User.objects.filter(email=email).exclude(id=user_id).count() > 0:
      self.add_error('email', 'This email is already taken. Please choose another.')
      valid = False

    return valid


####################################
# Student Form
####################################
class StudentForm (ModelForm):
  class Meta:
    model = models.Student
    fields = ['school', 'consent', 'test_account']
    widgets = {
      'consent': forms.RadioSelect(),
      'school': autocomplete.ModelSelect2(url='school-autocomplete', attrs={'data-placeholder': 'Start typing the school name ...',})
    }

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(StudentForm, self).__init__(*args, **kwargs)
    if user.is_authenticated:
      if hasattr(user, 'school_administrator'):
        school = user.school_administrator.school
      elif hasattr(user, 'teacher'):
        school = user.teacher.school
      elif hasattr(user, 'student'):
        school = user.student.school
      else:
        school = None

      if school is not None:
        self.fields['school'].queryset = models.School.objects.filter(id=school.id)
      else:
        self.fields['school'].queryset = models.School.objects.filter(~Q(school_code='OTHER'), is_active=True).order_by('name')

      if hasattr(user, 'student') == False:
        self.fields.pop('consent')
      else:
        self.fields.pop('test_account')

    for field_name, field in list(self.fields.items()):
      if field_name != 'consent':
        field.widget.attrs['class'] = 'form-control'
        field.widget.attrs['aria-describedby'] = field.label
        field.widget.attrs['placeholder'] = field.help_text
        if field_name == 'test_account':
          field.label = 'Test Account?'
      else:
        field.label = 'Online Consent'

####################################
# Consent Form
####################################
class ConsentForm (ModelForm):

  class Meta:
    model = models.Student
    fields = ['consent']
    widgets = {
      'consent': forms.RadioSelect()
    }


####################################
# Teacher Form
####################################
class TeacherForm (ModelForm):
  class Meta:
    model = models.Teacher
    fields = ['school']
    widgets = {
      'school': autocomplete.ModelSelect2(url='school-autocomplete', attrs={'data-placeholder': 'Start typing the school name ...',})
    }

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(TeacherForm, self).__init__(*args, **kwargs)

    if user.is_authenticated:
      if hasattr(user, 'school_administrator'):
        school = user.school_administrator.school
      elif hasattr(user, 'teacher'):
        school = user.teacher.school
      else:
        school = None

      if school is not None:
        self.fields['school'].queryset = models.School.objects.filter(id=school.id)
      else:
        self.fields['school'].queryset = models.School.objects.filter(~Q(school_code='OTHER'), is_active=True).order_by('name')

    else:
      self.fields['school'].queryset = models.School.objects.all().filter(is_active=True)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Researcher Form
####################################
class ResearcherForm (ModelForm):
  class Meta:
    model = models.Researcher
    fields = []
  def __init__(self, *args, **kwargs):
    super(ResearcherForm, self).__init__(*args, **kwargs)
    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text

####################################
# School Administrator Form
####################################
class SchoolAdministratorForm (ModelForm):
  class Meta:
    model = models.SchoolAdministrator
    fields = ['school']
  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(SchoolAdministratorForm, self).__init__(*args, **kwargs)
    if user.is_authenticated and hasattr(user, 'school_administrator'):
      school = user.school_administrator.school
      self.fields['school'].queryset = models.School.objects.filter(id=school.id)
    else:
      self.fields['school'].queryset = models.School.objects.filter(~Q(school_code='OTHER'), is_active=True).order_by('name')

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Author Form
####################################
class AuthorForm (ModelForm):
  class Meta:
    model = models.Author
    fields = []
  def __init__(self, *args, **kwargs):
    super(AuthorForm, self).__init__(*args, **kwargs)
    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text
####################################
# Curriculum Form
####################################
class CurriculumForm(ModelForm):

  class Meta:
    model = models.Curriculum
    fields = ['curriculum_type', 'unit', 'order', 'feature_rank', 'title', 'icon', 'time', 'level', 'overview', 'student_overview', 'acknowledgement', 'credits', 'status', 'subject', 'taxonomy', 'teacher_notes']

    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'Lesson Title'}),
      'time': forms.TextInput(attrs={'rows':0, 'cols':60}),
      'level': forms.TextInput(attrs={'rows':0, 'cols':60}),
      'overview': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'student_overview': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'content': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'teacher_notes': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'taxonomy': forms.SelectMultiple(attrs={'size':5}),
      'subject': forms.CheckboxSelectMultiple(),
      'acknowledgement': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'credits': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'icon': widgets.FileInput,
    }

  def __init__(self, *args, **kwargs):
    usr = kwargs.pop('user')
    page = kwargs.pop('page')
    super(CurriculumForm, self).__init__(*args, **kwargs)
    forms.ModelForm.__init__(self, *args, **kwargs)

    if page == 0:
      self.fields.pop('curriculum_type')
      self.fields.pop('unit')
      self.fields.pop('order')
      self.fields.pop('feature_rank')
      self.fields.pop('title')
      self.fields.pop('icon')
      self.fields.pop('time')
      self.fields.pop('level')
      self.fields.pop('overview')
      self.fields.pop('acknowledgement')
      self.fields.pop('credits')
      self.fields.pop('status')
      self.fields.pop('subject')
      self.fields.pop('taxonomy')
      self.fields.pop('teacher_notes')
    else:
      self.fields.pop('student_overview')
      self.fields['taxonomy'].label = "Standards"
      self.fields['order'].label = "Curriculum Order"
      self.fields['unit'].queryset = models.Curriculum.objects.filter(curriculum_type='U').order_by(Lower('title'), 'version')
      self.fields['unit'].label_from_instance = lambda obj: "%s - v%d." % (obj.title, obj.version)
      if hasattr(usr, 'teacher'):
        self.fields['unit'].queryset = models.Curriculum.objects.filter(curriculum_type='U', curriculumcollaborator__user=usr, curriculumcollaborator__privilege='E').order_by(Lower('title'), 'version')
        self.fields.pop('feature_rank')
        if self.instance.id and self.instance.status == 'P':
          self.fields['status'].choices = models.CURRICULUM_STATUS_CHOICES[:3]
        else:
          self.fields['status'].choices = models.CURRICULUM_STATUS_CHOICES[:1] + models.CURRICULUM_STATUS_CHOICES[2:3]
      else:
        self.fields['status'].choices = models.CURRICULUM_STATUS_CHOICES[:3]

      if self.instance.id:
        self.fields['curriculum_type'].widget.attrs['disabled'] = True

    for field_name, field in list(self.fields.items()):
      if field_name == 'order' or field_name == 'feature_rank':
        field.widget.attrs['class'] = 'form-control order'
      else:
        field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

  def is_valid(self, page):
    valid = super(CurriculumForm, self).is_valid()
    if not valid:
      return valid

    cleaned_data = super(CurriculumForm, self).clean()
    if page == 0:
      if cleaned_data.get('student_overview') == '' or cleaned_data.get('student_overview') is None:
        self.add_error('student_overview', 'Student Directions & Learning Objectives is required')
        valid = False
    else:
      if cleaned_data.get('icon'):
        try:
          cleaned_data.get('icon').read()
          validateImage(cleaned_data.get('icon'), 400, 289)
        except IOError as e:
          self.add_error('icon', 'Icon file is invalid. Please upload a new icon.')
          valid = False
        except ValidationError as e:
          self.add_error('icon', e.message)
          valid = False

      if cleaned_data.get('title') == '' or cleaned_data.get('title') is None:
        self.add_error('title', 'Title is required')
        valid = False
      if cleaned_data.get('time') == '' or cleaned_data.get('time') is None:
        self.add_error('time', 'Time is required')
        valid = False
      if not cleaned_data.get('unit'):
        if cleaned_data.get('level') == '' or cleaned_data.get('level') is None:
          self.add_error('level', 'Level is required')
          valid = False
        if cleaned_data.get('overview') == '' or cleaned_data.get('overview') is None:
          self.add_error('overview', 'Overview is required')
          valid = False
        if not cleaned_data.get('taxonomy'):
            self.add_error('taxonomy', 'Standards is required')
            valid = False

      if cleaned_data.get('curriculum_type') == 'U'  or cleaned_data.get('curriculum_type') == 'L':
        if not cleaned_data.get('unit'):
          if not cleaned_data.get('subject'):
            self.add_error('subject', 'Subject is required')
            valid = False

      if cleaned_data.get('status') == 'A':
        inprogress_assignments = None
        if cleaned_data.get('curriculum_type') == 'U':
          unit = self.instance
          lessons = unit.underlying_curriculum.all()
          inprogress_assignments = models.AssignmentInstance.objects.all().filter(assignment__curriculum__in=lessons, status='P')
        else:
          lesson = self.instance
          inprogress_assignments = models.AssignmentInstance.objects.all().filter(assignment__curriculum=lesson, status='P')

        if inprogress_assignments:
          self.add_error('status', 'You cannot archive this curriculum at this time because there may be students currently working on it. \
                                    Archiving will affect all students and teachers who have assigned this curriculum. Please try again later.')
          valid = False

    return valid

####################################
# Curriculum Step Form
####################################
class StepForm(ModelForm):

  class Meta:
    model = models.Step
    exclude = ('curriculum',)
    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'Step Title'}),
      'content': forms.Textarea(attrs={'rows':0, 'cols':60}),
    }

  def __init__(self, *args, **kwargs):
    super(StepForm, self).__init__(*args, **kwargs)
    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text


####################################
# Lesson Attachment Form
####################################
class AttachmentForm(ModelForm):

  class Meta:
    model = models.Attachment
    fields = ['title', 'file_object']
    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'Activity Title'}),
      'file_object': widgets.NotClearableFileInput,
    }

  def __init__(self, *args, **kwargs):
    super(AttachmentForm, self).__init__(*args, **kwargs)
    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

  def is_valid(self):
    valid = super(AttachmentForm, self).is_valid()
    if not valid:
      return valid

    cleaned_data = super(AttachmentForm, self).clean()

    if cleaned_data.get('file_object') and not cleaned_data.get('DELETE'):
      try:
        cleaned_data.get('file_object').read()
      except IOError as e:
        self.add_error('file_object', 'Attached file is invalid. Please upload a new attachment.')
        valid = False

    return valid

class CollaboratorInlineFormSet(BaseInlineFormSet):

  def clean(self):
    super(CollaboratorInlineFormSet, self).clean()

    if not self.instance.unit:
      author_count = 0
      for form in self.forms:
        if not form.is_valid():
          continue
        if form.cleaned_data and not form.cleaned_data.get('DELETE'):
          if form.cleaned_data['privilege'] == 'E':
            author_count += 1

      if author_count == 0:
        error = ValidationError("At least one collaborator with edit privilege is required.", "error")
        self._non_form_errors.append(error)

####################################
# Curriculum Collaborator Form
####################################
class CurriculumCollaboratorForm(ModelForm):

  class Meta:
    model = models.CurriculumCollaborator
    exclude = ('order',)

  def __init__(self, *args, **kwargs):
    super(CurriculumCollaboratorForm, self).__init__(*args, **kwargs)
    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Curriculum Question Form
####################################
class CurriculumQuestionForm(ModelForm):

  class Meta:
    model = models.CurriculumQuestion
    exclude = ('order',)

####################################
#  Question Form
####################################
class QuestionForm(ModelForm):

  class Meta:
    model = models.Question
    fields = ['research_category', 'question_text', 'answer_field_type', 'sketch_background', 'options', 'display_other_option', 'answer', 'is_active']
    widgets = {
      'question_text': forms.TextInput(attrs={'placeholder': 'Enter question here'}),
      'options': forms.Textarea(attrs={'rows':5, 'cols':60}),
      'answer': forms.Textarea(attrs={'rows':5, 'cols':60, 'placeholder': 'Answer if applicable'}),
    }
    error_messages ={
      'question_text': {
        'required': 'Question Text is required'
      }
    }

  def __init__(self, *args, **kwargs):
    disable_fields = False
    if 'disable_fields' in kwargs:
      disable_fields = kwargs.pop('disable_fields')

    super(QuestionForm, self).__init__(*args, **kwargs)

    if disable_fields:
      self.fields['answer_field_type'].widget.attrs['disabled'] = True
      self.fields['options'].widget.attrs['disabled'] = True

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'

  def is_valid(self):
    valid = super(QuestionForm, self).is_valid()

    cleaned_data = super(QuestionForm, self).clean()

    if cleaned_data.get('research_category').count() == 0:
      self.add_error('research_category', 'Select at least one Research Category for this question.')
      valid = False
    if cleaned_data.get('sketch_background'):
      try:
        cleaned_data.get('sketch_background').read()
        validateImage(cleaned_data.get('sketch_background'), 900, 500)
      except IOError as e:
        self.add_error('sketch_background', 'Background image file is invalid. Please upload a new file.')
        valid = False
      except ValidationError as e:
        self.add_error('sketch_background', e.message)
        valid = False
    if cleaned_data.get('answer_field_type') in ['DD', 'MC', 'MS', 'MI', 'MH', 'DT'] and cleaned_data.get('options') == '':
      self.add_error('options', 'Options is required for %s'% dict(self.fields['answer_field_type'].choices)[cleaned_data.get('answer_field_type')])
      valid = False

    return valid

####################################
# Question Search Form
####################################
class QuestionSearchForm(forms.Form):
  page_number = forms.IntegerField(required=False)
  question_number = forms.IntegerField(required=False)
  answer_field_type = forms.ChoiceField(required = False, choices=(('','------------'),) + models.FIELD_TYPE_CHOICES)
  research_category = forms.ModelChoiceField(required = False, queryset=models.ResearchCategory.objects.all())
  question_text = forms.CharField(required = False, widget=forms.Textarea(attrs={'rows': 2, 'cols': 60, 'placeholder': 'Question text'}))
  only_my_questions = forms.BooleanField(required=False)

  def __init__(self, *args, **kwargs):
    super(QuestionSearchForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      if field_name == 'page_number' or field_name == 'question_number':
        field.widget.attrs['class'] = 'form-control order'
      else:
        field.widget.attrs['class'] = 'form-control'

      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text


####################################
#  Research Category Form
####################################
class ResearchCategoryForm(ModelForm):

  class Meta:
    model = models.ResearchCategory
    fields = ['category', 'description', 'abbrevation', 'flag']
    widgets = {
      'category': forms.TextInput(attrs={'placeholder': 'Enter category here'}),
      'description': forms.Textarea(attrs={'rows':5, 'cols':60, 'placeholder': 'Category description'}),
      'abbrevation': forms.TextInput(attrs={'placeholder': 'Enter abbrevation here'}),
    }
    labels = {
      'abbrevation': 'Abbreviation'
    }

  def __init__(self, *args, **kwargs):
    super(ResearchCategoryForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      #field.widget.attrs['placeholder'] = field.help_text

####################################
# Subcategory Form
####################################
class SubcategoryForm(ModelForm):

  class Meta:
    model = models.Subcategory
    exclude = ('id',)
    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'Subcategory title'}),
      'code': forms.TextInput(attrs={'placeholder': 'Subcategory code'}),
      'description': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'link': forms.TextInput(attrs={'placeholder': 'URL'}),
    }

  def __init__(self, *args, **kwargs):
    super(SubcategoryForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text

####################################
# Taxonomy Search Form
####################################
class TaxonomySearchForm(forms.Form):
  standard = forms.ModelChoiceField(required = False, queryset=models.Standard.objects.all())
  category = forms.ModelChoiceField(required = False, queryset=models.Category.objects.none())
  title = forms.CharField(required = False, widget=forms.TextInput(attrs={'placeholder': 'Standards title'}))
  code = forms.CharField(required = False, widget=forms.TextInput(attrs={'placeholder': 'Standards code'}))

  def __init__(self, *args, **kwargs):
    super(TaxonomySearchForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text

      if field_name == 'category':
        field.queryset = models.Category.objects.none()

####################################
# User Search Form
####################################
class UserSearchForm(forms.Form):
  username = forms.CharField(required=False, max_length=30, label='Username')
  first_name = forms.CharField(required=False, max_length=30, label='First name')
  last_name = forms.CharField(required=False, max_length=30, label='Last name')
  email = forms.EmailField(required=False, max_length=75, label='Email')

  def __init__(self, *args, **kwargs):
    super(UserSearchForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text


####################################
# Create and Add Student Form
####################################
class StudentAddForm(forms.Form):

  username = forms.RegexField(required=True, regex=r'^\w+$', max_length=30, label='Username',
                              error_messages={'invalid': 'Usernames may only contain letters, numbers, and underscores (_)'})
  first_name = forms.CharField(required=True, max_length=30, label='First name')
  last_name = forms.CharField(required=True, max_length=30, label='Last name')
  email = forms.EmailField(required=True, max_length=75, label='Email')
  test_account = forms.BooleanField(required=False, label='Test Account?')

  def __init__(self, *args, **kwargs):
    super(StudentAddForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      if field.required:
        field.widget.attrs['required'] = 'required'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text

  def clean_username(self):
    return self.cleaned_data['username'].lower().strip()

  def clean_email(self):
    return self.cleaned_data['email'].lower().strip()


  def clean(self):
    cleaned_data = super(StudentAddForm, self).clean()
    username = cleaned_data.get('username')
    first_name = cleaned_data.get('first_name')
    last_name = cleaned_data.get('last_name')
    email = cleaned_data.get('email')
    test_account = cleaned_data.get('test_account')

    if username is None:
      self.fields['username'].widget.attrs['class'] += ' error'
    elif User.objects.filter(username=username.lower()).count() > 0:
      self.add_error('username', 'This username is already taken. Please choose another.')
      self.fields['username'].widget.attrs['class'] += ' error'

    if first_name is None:
      self.fields['first_name'].widget.attrs['class'] += ' error'
    if last_name is None:
      self.fields['last_name'].widget.attrs['class'] += ' error'
    if email is None:
      self.fields['email'].widget.attrs['class'] += ' error'
    elif User.objects.filter(email=email).count() > 0:
      self.add_error('email', 'This email is already taken. Please choose another.')
      self.fields['email'].widget.attrs['class'] += ' error'

####################################
# Assignment Search Form
####################################
class AssignmentSearchForm(forms.Form):

  group_class = forms.ModelChoiceField(queryset=models.UserGroup.objects.all().filter(is_active=True).order_by(Lower('title')))
  curriculum_type = forms.ChoiceField(choices=(('', '---------'),)+models.CURRICULUM_TYPE_CHOICES, required=False)
  title = forms.CharField(max_length=256, required=False)
  subject = forms.ModelChoiceField(queryset=models.Subject.objects.all(), required=False)

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(AssignmentSearchForm, self).__init__(*args, **kwargs)
    if hasattr(user, 'teacher'):
      self.fields['group_class'].queryset = self.fields['group_class'].queryset.filter(Q(teacher=user.teacher) | Q(shared_with=user.teacher))
    elif hasattr(user, 'school_administrator'):
      self.fields['group_class'].queryset = self.fields['group_class'].queryset.filter(teacher__school=user.school_administrator.school)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text


####################################
# Assignment Grouping Form
####################################
class AssignmentGroupingForm(forms.Form):

  group_by = forms.ChoiceField(choices=(('C', 'Group by Curriculum'),('G', 'Group by Class'),), required=False)

  def __init__(self, *args, **kwargs):

    super(AssignmentGroupingForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text


########################################################
# Assignment Search Form on Teacher Assignment Dashboard
########################################################
class TeacherAssignmentDashboardSearchForm(forms.Form):
  assignment = forms.ModelChoiceField(queryset=models.Curriculum.objects.all(), required=False, label="Filter by Assigned Curriculum")
  sort_by = forms.ChoiceField(choices=(('', '---------'),
                                       ('curriculum', 'Assigned Curriculum'),
                                       ('last_opened', 'Last Opened'),
                                       ('assigned_date', 'Assigned Date'),
                                       ('class', 'Class')
                                       ), required=False)
  group = forms.ModelChoiceField(queryset=models.UserGroup.objects.all(), label="Filter by Class", required=False)

  def __init__(self, *args, **kwargs):
    group_id = None
    teacher = kwargs.pop('teacher')
    is_active = kwargs.pop('is_active')
    if 'group_id' in kwargs:
      group_id = kwargs.pop('group_id')

    super(TeacherAssignmentDashboardSearchForm, self).__init__(*args, **kwargs)
    groups = models.UserGroup.objects.all().filter(Q(is_active=is_active), Q(teacher=teacher) | Q(shared_with=teacher)).distinct().order_by(Lower('title'))
    self.fields['group'].queryset = groups

    if group_id:
      groups = models.UserGroup.objects.all().filter(id=group_id)
      self.fields['group'].initial = group_id

    #if group is selected, limit assignments from that group
    curricula = models.Curriculum.objects.all().filter(Q(unit__isnull=True), Q(assignments__group__in=groups) | Q(underlying_curriculum__assignments__group__in=groups)).distinct().order_by(Lower('title'))
    self.fields['assignment'].queryset = curricula #models.Assignment.objects.all().filter(group__in=groups).distinct().order_by('curriculum__title')
    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text


########################################################
# Assignment Search Form on Teacher Student Dashboard
########################################################
class TeacherStudentDashboardSearchForm(forms.Form):
  student = forms.ModelChoiceField(queryset=models.Student.objects.all(), required=False, label='Filter by Student')
  assignment = forms.ModelChoiceField(queryset=models.Curriculum.objects.all(), required=False, label='Filter by Assigned Curriculum')
  group = forms.ModelChoiceField(queryset=models.UserGroup.objects.all(), required=False, label='Filter by Class')
  sort_by = forms.ChoiceField(choices=(('', '---------'),)+models.STUDENT_DASHBOARD_SORT, required=True,  initial='student_last_first', label='Sort by')

  def __init__(self, *args, **kwargs):
    group_id = None
    user = kwargs.pop('user')
    teacher = kwargs.pop('teacher')
    is_active = kwargs.pop('is_active')
    if 'group_id' in kwargs:
      group_id = kwargs.pop('group_id')

    super(TeacherStudentDashboardSearchForm, self).__init__(*args, **kwargs)
    groups = models.UserGroup.objects.all().filter(Q(is_active=is_active), Q(teacher=teacher) | Q(shared_with=teacher)).distinct().order_by(Lower('title'))
    self.fields['group'].queryset = groups
    if group_id:
      groups = models.UserGroup.objects.all().filter(id=group_id)
      self.fields['group'].initial = group_id
    #if group is selected, limit students and assignments from that group
    students = models.Student.objects.all().filter(student_membership__group__in=groups).distinct()
    student_choices = [('', '---------')]
    if hasattr(user, 'researcher'):
      students = students.order_by('id')
      for stud in students:
        student_choices.append((stud.user.id, stud.user.id))
    else:
      students = students.order_by(Lower('user__last_name'), Lower('user__first_name'))
      for stud in students:
        student_choices.append((stud.user.id, stud))

    self.fields['student'].choices = tuple(student_choices)

    curricula = models.Curriculum.objects.all().filter(Q(unit__isnull=True), Q(assignments__group__in=groups) | Q(underlying_curriculum__assignments__group__in=groups)).distinct().order_by(Lower('title'))
    self.fields['assignment'].queryset = curricula #models.Assignment.objects.all().filter(group__in=groups).distinct().order_by('curriculum__title')
    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text

    if hasattr(user, 'researcher'):
      self.fields['sort_by'].choices =  (('', '---------'),) + models.STUDENT_DASHBOARD_SORT[:1] + models.STUDENT_DASHBOARD_SORT[5:]
    else:
      self.fields['sort_by'].choices =  (('', '---------'),) + models.STUDENT_DASHBOARD_SORT[1:]


####################################
# Student Inbox Filter Form
####################################
class InboxFilterForm (forms.Form):
  bucket = forms.ChoiceField(required=True, choices=(('active', 'Active'), ('archived', 'Archived')), initial='active', label='Folder', widget=forms.RadioSelect())
  group = forms.ModelChoiceField(required=False, queryset=models.UserGroup.objects.all().order_by(Lower('title')), label='Class')
  assignment = forms.ChoiceField(required=False, choices=(('', '---------'),), label='Assignment')
  teacher = forms.ModelChoiceField(required=False, queryset=models.Teacher.objects.all().filter().order_by(Lower('user__last_name'), Lower('user__first_name')), label='Teacher')
  sort_by = forms.ChoiceField(required=False, choices=models.ASSIGNMENT_SORT, initial='title', label='Sort by')

  def __init__(self, *args, **kwargs):
    student_id = group_id = curr_id = teacher_id = None
    if 'student_id' in kwargs:
      student_id = kwargs.pop('student_id')
    if 'group_id' in kwargs:
      group_id = kwargs.pop('group_id')
    if 'curr_id' in kwargs:
      curr_id = kwargs.pop('curr_id')
    if 'teacher_id' in kwargs:
      teacher_id = kwargs.pop('teacher_id')
    super(InboxFilterForm, self).__init__(*args, **kwargs)

    #populating classes and initial select
    #expand underlying curricula under unit
    groups = models.Membership.objects.all().filter(student__id=student_id).values_list('group', flat=True)
    if group_id:
      self.fields['group'].initial = group_id

    assignment_choices = util.group_assignment_dropdown_list(groups)
    self.fields['assignment'].choices = tuple(assignment_choices)
    if curr_id:
      self.fields['assignment'].initial = curr_id

    #populating teachers and initial select
    teachers = models.Teacher.objects.all().filter(Q(groups__id__in=groups) | Q(shared_groups__id__in=groups)).distinct()
    self.fields['teacher'].queryset = teachers
    if teacher_id:
      self.fields['teacher'].initial = teacher_id

    for field_name, field in list(self.fields.items()):
      if field_name != 'bucket':
        field.widget.attrs['class'] = 'form-control'
        field.widget.attrs['placeholder'] = field.help_text

####################################
# Assignment Progress Dashboard Search Form
####################################
class ProgressDashboardSearchForm(forms.Form):
  group = forms.ModelChoiceField(required=True, queryset=models.UserGroup.objects.all().order_by('title'), label='Class', empty_label=None)
  assignment = forms.ChoiceField(required=True, choices=(('', '---------'),), label='Assigned Curriculum', widget=widgets.SelectWithDisabled)
  sort_by = forms.ChoiceField(required=True, choices=models.PROGRESS_DASHBOARD_SORT, initial='title', label='Sort by')

  def __init__(self, *args, **kwargs):
    user = teacher_id = group_id = curriculum_id = None
    if 'user' in kwargs:
      user = kwargs.pop('user')
    if 'teacher_id' in kwargs:
      teacher_id = kwargs.pop('teacher_id')
    if 'group_id' in kwargs:
      group_id = kwargs.pop('group_id')
    if 'curriculum_id' in kwargs:
      curriculum_id = kwargs.pop('curriculum_id')

    super(ProgressDashboardSearchForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

    #populating classes and initial select
    #expand underlying curricula under unit
    teacher = models.Teacher.objects.get(id=teacher_id)
    selected_group = models.UserGroup.objects.all().filter(id=group_id)
    groups = models.UserGroup.objects.all().filter(Q(is_active=selected_group[0].is_active), Q(teacher=teacher) | Q(shared_with=teacher)).distinct().order_by(Lower('title'))
    self.fields['group'].queryset = groups
    self.fields['group'].initial = selected_group[0].id
    assignment_choices = util.group_assignment_dropdown_list(selected_group, False, False)
    self.fields['assignment'].choices = tuple(assignment_choices)
    if curriculum_id:
      self.fields['assignment'].initial = curriculum_id
    else:
      self.fields['assignment'].widget.attrs['class'] += ' error'

    if hasattr(user, 'researcher'):
      self.fields['sort_by'].choices =  models.PROGRESS_DASHBOARD_SORT[:1] + models.PROGRESS_DASHBOARD_SORT[3:]
    else:
      self.fields['sort_by'].choices =  models.PROGRESS_DASHBOARD_SORT[1:]

####################################
# Student Feedback Search Form
####################################
class StudentFeedbackSearchForm(forms.Form):
  group = forms.ModelChoiceField(required=True, queryset=models.UserGroup.objects.all().order_by('title'), label='Class', empty_label=None)
  assignment = forms.ChoiceField(required=True, choices=(('', '---------'),), label='Assigned Curriculum', widget=widgets.SelectWithDisabled)
  student = forms.ChoiceField(required=True, choices=(('', '---------'),), label='Filter by Student')

  def __init__(self, *args, **kwargs):
    user = teacher_id = group_id = curriculum_id = student_id = None
    if 'user' in kwargs:
      user = kwargs.pop('user')
    if 'teacher_id' in kwargs:
      teacher_id = kwargs.pop('teacher_id')
    if 'group_id' in kwargs:
      group_id = kwargs.pop('group_id')
    if 'curriculum_id' in kwargs:
      curriculum_id = kwargs.pop('curriculum_id')
    if 'student_id' in kwargs:
      student_id = kwargs.pop('student_id')

    super(StudentFeedbackSearchForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

    #populating classes and initial select
    teacher = models.Teacher.objects.get(id=teacher_id)
    selected_group = models.UserGroup.objects.all().filter(id=group_id)
    groups = models.UserGroup.objects.all().filter(Q(is_active=selected_group[0].is_active), Q(teacher=teacher) | Q(shared_with=teacher)).order_by(Lower('title'))
    students = models.Student.objects.all().filter(student_membership__group__id=group_id).distinct()
    if hasattr(user, 'researcher'):
      students = students.filter(consent='A').order_by('user__id')
    else:
      students = students.order_by(Lower('user__last_name'), Lower('user__first_name'))

    self.fields['group'].queryset = groups

    self.fields['group'].initial = selected_group[0].id

    #populating assignments and initial select
    assignment_choices = util.group_assignment_dropdown_list(selected_group, False, True)
    student_choices = None

    self.fields['assignment'].choices = tuple(assignment_choices)
    if curriculum_id:
      assignment = models.Assignment.objects.all().filter(group__id=group_id, curriculum__id=curriculum_id)[0]
      self.fields['assignment'].initial = curriculum_id
      anonymize = False
      if hasattr(user, 'researcher') or assignment.anonymize_student:
        anonymize = True
      student_choices = util.student_dropdown_list(students, anonymize)
      if student_id:
        self.fields['student'].initial = student_id
      else:
        self.fields['student'].widget.attrs['class'] += ' error'
    else:
      self.fields['assignment'].widget.attrs['class'] += ' error'
      self.fields['student'].widget.attrs['disabled'] = True
      student_choices = (('', '---------'),)

    #populating students and initial select
    self.fields['student'].choices = tuple(student_choices)



####################################
# Question Feedback Search Form
####################################
class QuestionFeedbackSearchForm(forms.Form):
  group = forms.ModelChoiceField(required=True, queryset=models.UserGroup.objects.all().order_by('title'), label='Class', empty_label=None)
  assignment = forms.ChoiceField(required=True, choices=(('', '---------'),), label='Assigned Curriculum', widget=widgets.SelectWithDisabled)
  question = forms.ChoiceField(required=True, choices=(('', '---------'),), label='Filter by Question')

  def __init__(self, *args, **kwargs):
    teacher_id = group_id = assignment_id = question_id = None
    if 'teacher_id' in kwargs:
      teacher_id = kwargs.pop('teacher_id')
    if 'group_id' in kwargs:
      group_id = kwargs.pop('group_id')
    if 'curriculum_id' in kwargs:
      curriculum_id = kwargs.pop('curriculum_id')
    if 'question_id' in kwargs:
      question_id = kwargs.pop('question_id')

    super(QuestionFeedbackSearchForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

    #populating classes and initial select
    teacher = models.Teacher.objects.get(id=teacher_id)
    selected_group = models.UserGroup.objects.all().filter(id=group_id)
    groups = models.UserGroup.objects.all().filter(Q(is_active=selected_group[0].is_active), Q(teacher=teacher) | Q(shared_with=teacher)).order_by(Lower('title'))

    self.fields['group'].queryset = groups
    self.fields['group'].initial = selected_group[0].id

    #populating assignments and initial select
    assignment_choices = util.group_assignment_dropdown_list(selected_group, False, True)
    question_choices = None

    self.fields['assignment'].choices = tuple(assignment_choices)
    if curriculum_id:
      self.fields['assignment'].initial = curriculum_id
      curriculum_questions = models.CurriculumQuestion.objects.all().filter(step__curriculum__id=curriculum_id).order_by('step__order', 'order')
      question_choices = util.question_dropdown_list(curriculum_questions)
      if question_id:
        self.fields['question'].initial = question_id
      else:
        self.fields['question'].widget.attrs['class'] += ' error'
    else:
      self.fields['assignment'].widget.attrs['class'] += ' error'
      self.fields['question'].widget.attrs['disabled'] = True
      question_choices = (('', '---------'),)

    #populating questions and initial select
    self.fields['question'].choices = tuple(question_choices)


####################################
# Search Form
####################################
class SearchForm(forms.Form):
  search_criteria = forms.CharField(required=False, max_length=30, label='Search Criteria', help_text='Enter your search text')

  def __init__(self, *args, **kwargs):
    super(SearchForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text


####################################
# Curricula Search Form
####################################
class CurriculaSearchForm(forms.Form):
  subjects = forms.ModelMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple(), queryset=models.Subject.objects.all().order_by('name'))
  curricula_types = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple(), choices=models.CURRICULUM_TYPE_CHOICES)
  buckets = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple(), choices=models.CURRICULUM_BUCKET_CHOICES, label='My Collections')
  status = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple(), choices=models.CURRICULUM_STATUS_CHOICES)
  keywords = forms.CharField(required=False, max_length=60, label=u'Search by Keyword')
  sort_by = forms.ChoiceField(required=False, choices=(('', '---------'),)+models.CURRICULA_SORT_CHOICES)

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(CurriculaSearchForm, self).__init__(*args, **kwargs)

    if user.is_anonymous or hasattr(user, 'student') or hasattr(user, 'school_administrator'):
      self.fields.pop('status')
      self.fields.pop('buckets')
    elif hasattr(user, 'teacher'):
      self.fields['status'].choices = models.CURRICULUM_STATUS_CHOICES[:3]
      self.fields['buckets'].choices = models.CURRICULUM_BUCKET_CHOICES[1:]
    elif hasattr(user, 'researcher'):
      self.fields['status'].choices = models.CURRICULUM_STATUS_CHOICES[:3]
      self.fields['buckets'].choices = models.CURRICULUM_BUCKET_CHOICES[:3]
    else:
      self.fields['buckets'].choices = models.CURRICULUM_BUCKET_CHOICES[:1]
      if not hasattr(user, 'administrator'):
        self.fields['status'].choices = models.CURRICULUM_STATUS_CHOICES[:3]

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text

####################################
# Standards Form
####################################
class StandardForm(ModelForm):

  class Meta:
    model = models.Standard
    exclude = ('id',)
    widgets = {
      'name': forms.TextInput(attrs={'placeholder': 'Standard name'}),
    }

  def __init__(self, *args, **kwargs):
    super(StandardForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Standards Category Form
####################################
class CategoryForm(ModelForm):

  class Meta:
    model = models.Category
    exclude = ('id', 'standard', 'order')
    widgets = {
      'name': forms.TextInput(attrs={'placeholder': 'Category name'}),
      'description': forms.Textarea(attrs={'rows':0, 'cols':60}),
    }

  def __init__(self, *args, **kwargs):
    super(CategoryForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

  def is_valid(self):
    valid = super(CategoryForm, self).is_valid()
    if not valid:
      return valid

    cleaned_data = super(CategoryForm, self).clean()

    if cleaned_data.get('icon'):
      try:
        cleaned_data.get('icon').read()
        validateImage(cleaned_data.get('icon'), 400, 289)
      except IOError as e:
        self.add_error('icon',  'Icon file is invalid. Please upload a new file.')
        valid = False
      except ValidationError as e:
        self.add_error('icon', e.message)
        valid = False

    return valid
####################################
# Publication Form
####################################
class PublicationForm(ModelForm):

  class Meta:
    model = models.Publication
    exclude = ('created_date', 'modified_date')

  def __init__(self, *args, **kwargs):
    super(PublicationForm, self).__init__(*args, **kwargs)

    self.fields['journal'].label = 'Journal/Conference'

    for field_name, field in list(self.fields.items()):
      if field_name == 'order':
        field.widget.attrs['class'] = 'form-control order'
      else:
        field.widget.attrs['class'] = 'form-control'


####################################
# Release Note Form
####################################
class ReleaseNoteForm(ModelForm):

  class Meta:
    model = models.ReleaseNote
    fields = ['version', 'release_date']
    widgets = {
      'release_date': forms.DateInput(),
    }

  def __init__(self, *args, **kwargs):
    super(ReleaseNoteForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      if field_name == 'release_date':
        field.widget.attrs['class'] = 'form-control datepicker'
      else:
        field.widget.attrs['class'] = 'form-control'

class ReleaseChangeForm(ModelForm):
  class Meta:
    model = models.ReleaseChange
    fields = ['change_type', 'description']
    widgets = {
      'description': forms.Textarea(attrs={'rows':5, 'cols':60}),
      }

  def __init__(self, *args, **kwargs):
    super(ReleaseChangeForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'

####################################
# Topic Form
####################################
class TopicForm(ModelForm):

  class Meta:
    model = models.Topic
    fields = ['name', 'order']

  def __init__(self, *args, **kwargs):
    super(TopicForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      if field_name == 'order':
        field.widget.attrs['class'] = 'form-control order'
      else:
        field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Sub Topic Form
####################################
class SubTopicForm(ModelForm):

  class Meta:
    model = models.SubTopic
    fields = ['topic', 'name', 'description', 'order']
    widgets = {
      'description': forms.Textarea(attrs={'rows':0, 'cols':60}),
    }

  def __init__(self, *args, **kwargs):
    topic_type = kwargs.pop('topic_type')
    super(SubTopicForm, self).__init__(*args, **kwargs)
    self.fields['topic'].queryset = models.Topic.objects.all().filter(topic_type=topic_type)

    for field_name, field in list(self.fields.items()):
      if field_name == 'order':
        field.widget.attrs['class'] = 'form-control order'
      else:
        field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# User Group Form
####################################
class UserGroupForm(ModelForm):
  #members = forms.ModelMultipleChoiceField(required=False, queryset=models.Student.objects.all(), widget=FilteredSelectMultiple(('Members'), False, attrs={'size':5}))

  class Meta:
    model = models.UserGroup
    exclude = ('id',)
    widgets = {
      'icon': widgets.FileInput,
    }

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(UserGroupForm, self).__init__(*args, **kwargs)

    self.fields['title'].label = 'Class Name/Title'
    self.fields['time'].label = 'Time/Period'
    self.fields['shared_with'].label = 'Shared Teachers'
    self.fields['group_code'].label = 'Class Code'
    self.fields['is_active'].label = 'Class Status'
    self.fields['group_code'].widget.attrs['readonly'] = True
    if hasattr(user, 'teacher'):
      self.fields['members'].queryset = self.fields['members'].queryset.filter(school=user.teacher.school).order_by('user__first_name', 'user__last_name')
    elif hasattr(user, 'school_administrator'):
      self.fields['teacher'].queryset = self.fields['teacher'].queryset.filter(school=user.school_administrator.school).order_by('user__first_name', 'user__last_name')
      self.fields['members'].queryset = self.fields['members'].queryset.filter(school=user.school_administrator.school).order_by('user__first_name', 'user__last_name')

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

    #if group is inactive, disable all fields
    if self.instance.is_active == False:
      for field_name, field in list(self.fields.items()):
        if field_name == 'subject' or field_name == 'teacher':
          field.widget.attrs['disabled'] = True
        elif field_name != 'is_active':
          field.widget.attrs['readonly'] = True

  def is_valid(self):
    valid = super(UserGroupForm, self).is_valid()
    if not valid:
      return valid

    cleaned_data = super(UserGroupForm, self).clean()

    if cleaned_data.get('icon'):
      try:
        cleaned_data.get('icon').read()
        validateImage(cleaned_data.get('icon'), 400, 289)
      except IOError as e:
        self.add_error('icon', 'Icon file is invalid. Please upload a new file.')
        valid = False
      except ValidationError as e:
        self.add_error('icon', e.message)
        valid = False

    return valid

  def save(self, commit=True):
    instance = forms.ModelForm.save(self, False)

    def save_m2m():

      old_members = models.Membership.objects.filter(group=instance)
      for old_member in old_members:
        changed = True
        for curr_member in self.cleaned_data['members']:
            if old_member.student == curr_member:
                changed = False
        if changed:
            old_member.delete()

      for member in self.cleaned_data['members']:
        try:
            models.Membership.objects.get(group=instance, student=member)
        except models.Membership.DoesNotExist:
            membership = models.Membership(group=instance, student=member)
            membership.save()

      for teacher in self.cleaned_data['shared_with']:
        if teacher not in instance.shared_with.all():
          instance.shared_with.add(teacher)

      for teacher in instance.shared_with.all():
        if teacher not in self.cleaned_data['shared_with']:
          instance.shared_with.remove(teacher)

    self.save_m2m = save_m2m
    if commit:
        instance.save()
        self.save_m2m()

    return instance

####################################
# Assignment Form
####################################
class AssignmentForm(ModelForm):

  class Meta:
    model = models.Assignment
    exclude = ('group', 'assigned_date')
    #fields = ['id', 'curriculum', 'group', 'assigned_date', 'due_date']

  def __init__(self, *args, **kwargs):
    super(AssignmentForm, self).__init__(*args, **kwargs)
    self.fields["curriculum"].queryset = models.Curriculum.objects.filter(status='P')

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

  def get_assigned_date(self):
    if self.instance.id:
      return self.instance.assigned_date

####################################
# Curriculum Assignment Form
####################################
class CurriculumAssignmentForm(ModelForm):
  due_date = forms.DateField(widget=forms.DateInput(format='%b %d, %Y'), input_formats=['%b %d, %Y'])
  assigned_date = forms.DateField(widget=forms.DateInput(format='%b %d, %Y'), input_formats=['%b %d, %Y'])

  class Meta:
    model = models.Assignment
    exclude = ('curriculum', )

  def __init__(self, *args, **kwargs):
    super(CurriculumAssignmentForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      if field_name == 'due_date':
        field.widget.attrs['class'] = 'form-control datepicker'
        field.widget.attrs['readonly'] = True
      elif field_name =='assigned_date':
        if self.instance.id and self.instance.assigned_date.date() <= date.today():
          field.widget.attrs['class'] = 'form-control'
        else:
          field.widget.attrs['class'] = 'form-control datepicker'
        field.widget.attrs['readonly'] = True
      else:
        field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

  def get_assigned_date(self):
    if self.instance.id:
      return self.instance.assigned_date

####################################
# CSV Upload Form
####################################
class UploadFileForm(forms.Form):
  group = forms.ModelChoiceField(required=True, queryset=models.UserGroup.objects.all().filter(is_active=True))
  emails = forms.CharField(required=False, widget=forms.Textarea, help_text="Enter a list of student emails, one per line")
  uploadFile = forms.FileField (required=False, help_text="Upload a csv file containing a list of student emails in the first column")

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(UploadFileForm, self).__init__(*args, **kwargs)
    if user.is_authenticated:
      if hasattr(user, 'school_administrator'):
        self.fields['group'].queryset = models.UserGroup.objects.all().filter(teacher__school=user.school_administrator.school, is_active=True).distinct()
      elif hasattr(user, 'teacher'):
        self.fields['group'].queryset = models.UserGroup.objects.all().filter(Q(is_active=True), Q(teacher=user.teacher)| Q(shared_with=user.teacher)).distinct()
    else:
      self.fields['group'].queryset = models.UserGroup.objects.none()

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Instance Form
####################################
class AssignmentInstanceForm(ModelForm):
  class Meta:
    model = models.AssignmentInstance
    fields = ['teammates']

  def __init__(self, *args, **kwargs):
    assignment = kwargs.pop('assignment')

    super(AssignmentInstanceForm, self).__init__(*args, **kwargs)
    self.fields['teammates'].queryset = assignment.group.members.order_by('user__first_name', 'user__last_name')

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text

####################################
# AssignmentStepResponse Form
####################################
class AssignmentNotesForm(ModelForm):
  class Meta:
    model = models.AssignmentNotes
    exclude = ('instance',)

  def __init__(self, *args, **kwargs):
    super(AssignmentNotesForm, self).__init__(*args, **kwargs)
    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text

####################################
# AssignmentStepResponse Form
####################################
class AssignmentStepResponseForm(ModelForm):
  class Meta:
    model = models.AssignmentStepResponse
    exclude = ('instance', 'step',)


####################################
# QuestionResponse Form
####################################
class QuestionResponseForm(ModelForm):
  save = forms.BooleanField(required=False)

  class Meta:
    model = models.QuestionResponse
    exclude = ('created_date', 'modified_date',)

  def clean(self):
    cleaned_data = super(QuestionResponseForm, self).clean()
    uploaded_files = 0
    for form in self.nested:
      if form['id'].data or form['file'].data:
        if not form['DELETE'].data:
          uploaded_files += 1

    response = cleaned_data.get('response').strip()
    save = cleaned_data.get('save')
    curriculum_question = models.CurriculumQuestion.objects.get(id=cleaned_data.get('curriculum_question').id)

    # mandatory question validation when form submission is not a save and both the response field and the upload field are empty and the
    # question is not optional
    if save == False and not response and uploaded_files == 0 and not curriculum_question.optional:
      self.add_error('response', 'Please answer this question')
      self.nested[0].add_error('file', 'Please upload at least one file')
    if save == False and response and curriculum_question.question.answer_field_type in ('SK', 'DT') and not curriculum_question.optional:
      resp_list = ast.literal_eval(response)
      empty_response = util.is_list_empty(resp_list)
      if empty_response:
        if curriculum_question.question.answer_field_type == 'SK':
           self.add_error('response', 'Please draw a sketch')
        elif curriculum_question.question.answer_field_type == 'DT':
           self.add_error('response', 'Please fillout the table')

    if curriculum_question.question.answer_field_type in ('TA', 'TF') and len(response) > 30000:
      self.add_error('response', 'Your response cannot be longer than 30,000 characters')


####################################
# QuestionResponseFile Form
####################################
class QuestionResponseFileForm(ModelForm):
  class Meta:
    model = models.QuestionResponseFile
    fields = ['file']
    widgets = {
      'file': widgets.NotClearableFileInput,
    }

  def __init__(self, *args, **kwargs):
    super(QuestionResponseFileForm, self).__init__(*args, **kwargs)
    self.fields['file'].widget.attrs = {'id':'selectedFile'}
    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

  def clean(self):
    cleaned_data = super(QuestionResponseFileForm, self).clean()
    file = cleaned_data.get('file')
    delete = cleaned_data.get('DELETE')
    if not delete and file.size > 10*1024*1024:
      self.add_error('file', 'Uploaded file cannot be bigger than 10MB')

####################################
# Feedback Form
####################################
class FeedbackForm(ModelForm):
  class Meta:
    model = models.AssignmentFeedback
    exclude = ('instance',)

####################################
# Step Feedback Form
####################################
class StepFeedbackForm(ModelForm):

  class Meta:
    model = models.StepFeedback
    exclude = ('assignment_feedback', 'step_response',)

####################################
# Question Feedback Form
####################################
class QuestionFeedbackForm(ModelForm):

  class Meta:
    model = models.QuestionFeedback
    exclude = ('step_feedback', 'response', 'created_date', 'modified_date',)
    widgets = {
      'feedback': forms.Textarea(attrs={'rows':5, 'cols':60}),
    }

  def __init__(self, *args, **kwargs):
    super(QuestionFeedbackForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# School Form
####################################
class SchoolForm(ModelForm):

  class Meta:
    model = models.School
    exclude = ('id',)

  def __init__(self, *args, **kwargs):
    super(SchoolForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

      if field_name == 'name':
        field.label = 'School Name'
        field.error_messages = {'required':'School name is required'.format(
                fieldname=field.label)}
      elif field_name == 'city':
        field.error_messages = {'required':'School location is required'.format(
                fieldname=field.label)}

  def clean(self):
    cleaned_data = super(SchoolForm, self).clean()
    name = cleaned_data.get('name')
    city = cleaned_data.get('city')


    if name is None:
      self.fields['name'].widget.attrs['class'] += ' error'
    if city is None:
      self.fields['city'].widget.attrs['class'] += ' error'



####################################
# Subject Form
####################################
class SubjectForm(ModelForm):

  class Meta:
    model = models.Subject
    exclude = ('id',)
    labels = {
      'abbrevation': "Abbreviation"
    }

  def __init__(self, *args, **kwargs):
    super(SubjectForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

  def is_valid(self):
    valid = super(SubjectForm, self).is_valid()
    if not valid:
      return valid

    cleaned_data = super(SubjectForm, self).clean()

    if cleaned_data.get('icon'):
      try:
        cleaned_data.get('icon').read()
        validateImage(cleaned_data.get('icon'), 400, 289)
      except IOError as e:
        self.add_error('icon', 'Icon file is invalid. Please upload a new file.')
        valid = False
      except ValidationError as e:
        self.add_error('icon', e.message)
        valid = False

    return valid
####################################
# Team Role Form
####################################
class TeamRoleForm(ModelForm):

  class Meta:
    model = models.TeamRole
    exclude = ('id', 'order',)

  def __init__(self, *args, **kwargs):
    super(TeamRoleForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Team Member Form
####################################
class TeamMemberForm(ModelForm):

  class Meta:
    model = models.Team
    exclude = ('id',)
    labels = {
      'current': 'Current Member?',
    }

  def __init__(self, *args, **kwargs):
    super(TeamMemberForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Training Request Form
####################################
class TrainingRequestForm(ModelForm):

  class Meta:
    model = models.TrainingRequest
    exclude = ('id',)

  def __init__(self, *args, **kwargs):
    super(TrainingRequestForm, self).__init__(*args, **kwargs)

    for field_name, field in list(self.fields.items()):
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text
      field.error_messages['required'] = '{fieldname} is required'.format(fieldname=field.label)


  def clean(self):
    cleaned_data = super(TrainingRequestForm, self).clean()
    name = cleaned_data.get('name')
    email = cleaned_data.get('email')
    school = cleaned_data.get('school')
    subject = cleaned_data.get('subject')

    if name is None:
      self.fields['name'].widget.attrs['class'] += ' error'
    if email is None:
      self.fields['email'].widget.attrs['class'] += ' error'
    if school is None:
      self.fields['school'].widget.attrs['class'] += ' error'

    if subject is None:
      self.fields['subject'].widget.attrs['class'] += ' error'


  def is_valid(self):
    valid = super(TrainingRequestForm, self).is_valid()
    return valid

def validateImage(img, minwidth, minheight):
  image = Image.open(img)
  width, height = image.size
  print(width, height)
  if width < minwidth or height < minheight:
    raise ValidationError(_('Uploaded image is smaller than the minimum required resolution of %d x %d' % (minwidth, minheight)), code='invalid')
