from django import forms
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from ctstem_app import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory
from datetime import datetime
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.widgets import RadioSelect
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist
from tinymce.widgets import TinyMCE

####################################
# Registration Form
####################################
class RegistrationForm (forms.Form):
  username = forms.RegexField(required=True, regex=r'^\w+$', max_length=30, label=u'Username',
                              error_messages={'invalid': 'Usernames may only contain letters, numbers, and underscores (_)'})
  first_name = forms.CharField(required=True, max_length=30, label=u'First name')
  last_name = forms.CharField(required=True, max_length=30, label=u'Last name')
  password1 = forms.CharField(required=True, widget=forms.PasswordInput(render_value=False), label=u'Password')
  password2 = forms.CharField(required=True, widget=forms.PasswordInput(render_value=False), label=u'Confirm Password')
  email = forms.EmailField(required=True, max_length=75, label=u'Email')
  account_type = forms.ChoiceField(required=True, choices = models.USER_ROLE_CHOICES)
  school = forms.ModelChoiceField(required=False, queryset=models.School.objects.all())
  permission_code = forms.CharField(required=False, max_length=256, label=u'Permission code', help_text='Code shared by your teacher or school admin.')
  user_code = forms.CharField(required=False, max_length=256, label=u'User code', help_text='A unique code to share with your students or teachers')

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(RegistrationForm, self).__init__(*args, **kwargs)
    if user.is_authenticated():
      if hasattr(user, 'researcher'):
        self.fields['account_type'].choices = models.USER_ROLE_CHOICES[3:]
      elif hasattr(user, 'teacher'):
        self.fields['account_type'].choices = models.USER_ROLE_CHOICES[4:]
    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text


  def clean_username(self):
    if User.objects.filter(username=self.cleaned_data['username']).count() > 0:
      raise forms.ValidationError(u'This username is already taken. Please choose another.')
    return self.cleaned_data['username']

  def clean_email(self):
    if User.objects.filter(email=self.cleaned_data['email']).count() > 0:
      raise forms.ValidationError(u'This email address is already in use. Please supply a different email address.')
    return self.cleaned_data['email']

  def is_valid(self):
    valid = super(RegistrationForm, self).is_valid()
    if not valid:
      return valid

    clean = True
    error_list = []
    #check password
    if self.cleaned_data['password1'] != self.cleaned_data['password2']:
      error_list.append('P')
      self._errors['password1'] = u'Passwords are not identical'
      clean = False
    #check fields for Teacher
    if self.cleaned_data['account_type'] == 'T':
      if self.cleaned_data['school'] is None or self.cleaned_data['school'] == '':
        error_list.append('SR');
      if self.cleaned_data['permission_code'] is not None and self.cleaned_data['permission_code'] != '':
        try:
          models.Researcher.objects.get(user_code=self.cleaned_data['permission_code'], user__is_active=True)
        except models.Researcher.DoesNotExist:
          error_list.append('PI');
      if self.cleaned_data['user_code'] is None or self.cleaned_data['user_code'] == '':
        error_list.append('UR');
      else:
        try:
          models.Teacher.objects.get(user_code=self.cleaned_data['user_code'])
          error_list.append('UI');
        except models.Teacher.DoesNotExist:
          pass
    #check fields for Student
    elif self.cleaned_data['account_type'] == 'S':
      if self.cleaned_data['school'] is None or self.cleaned_data['school'] == '':
        error_list.append('SR');
      if self.cleaned_data['permission_code'] is not None and self.cleaned_data['permission_code'] != '':
        try:
          models.Teacher.objects.get(user_code=self.cleaned_data['permission_code'], user__is_active=True)
        except models.Teacher.DoesNotExist:
          error_list.append('PI');
    #check fields for Researcher
    elif self.cleaned_data['account_type'] == 'R':
      if self.cleaned_data['school'] is None or self.cleaned_data['school'] == '':
        error_list.append('SR');
      if self.cleaned_data['user_code'] is None or self.cleaned_data['user_code'] == '':
        error_list.append('UR');
      else:
        try:
          models.Researcher.objects.get(user_code=self.cleaned_data['user_code'])
          error_list.append('UI');
        except models.Researcher.DoesNotExist:
          pass
    if len(error_list) > 0:
      clean = False

    for error in error_list:
      if error == 'SR':
        self._errors['school'] = u'School is required'
      elif error == 'PI':
        self._errors['permission_code'] = u'Permission code is not valid'
      elif error == 'UR':
        self._errors['user_code'] = u'User code is required'
      elif error == 'UI':
        self._errors['user_code'] = u'User code is not unique'


    return clean

####################################
# UserProfile Form
####################################
class UserProfileForm(ModelForm):
  password1 = forms.CharField(widget=forms.PasswordInput, required=False, label=u'Password', help_text="Leave this field blank to retain old password")
  password2 = forms.CharField(widget=forms.PasswordInput, required=False, label=u'Confirm Password')

  class Meta:
    model = models.User
    fields = ["username","first_name", "last_name", "email", "password1", "password2", "is_active"]

  def __init__(self, *args, **kwargs):
    super(UserProfileForm, self).__init__(*args, **kwargs)
    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text

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

  def is_valid(self):
    valid = super(UserProfileForm, self).is_valid()
    if not valid:
      return valid

    if self.cleaned_data['password1'] != self.cleaned_data['password2']:
      self._errors['password1'] = u'Passwords are not identical'
      return False

    return True

####################################
# Student Form
####################################
class StudentForm (ModelForm):
  class Meta:
    model = models.Student
    fields = ['school']

  def __init__(self, *args, **kwargs):
    super(StudentForm, self).__init__(*args, **kwargs)
    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Teacher Form
####################################
class TeacherForm (ModelForm):
  class Meta:
    model = models.Teacher
    fields = ['school','students', 'user_code']

  def __init__(self, *args, **kwargs):
    super(TeacherForm, self).__init__(*args, **kwargs)
    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Researcher Form
####################################
class ResearcherForm (ModelForm):
  class Meta:
    model = models.Researcher
    fields = ['school','teachers', 'user_code']
  def __init__(self, *args, **kwargs):
    super(ResearcherForm, self).__init__(*args, **kwargs)
    for field_name, field in self.fields.items():
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
    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text
####################################
# Lesson Form
####################################
class LessonForm(ModelForm):
  #questions = forms.ModelMultipleChoiceField(required=False, queryset=models.Question.objects.all())#, widget=FilteredSelectMultiple(('Questions'), False, attrs={'size':15}))

  class Meta:
    model = models.Lesson
    fields = ['title', 'time', 'level', 'purpose', 'overview', 'status', 'subject', 'ngss_standards', 'ct_stem_practices', 'content', 'teacher_notes']
    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'Lesson Title'}),
      'time': forms.TextInput(attrs={'rows':0, 'cols':60}),
      'level': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'purpose': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'overview': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'content': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'teacher_notes': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'ngss_standards': forms.SelectMultiple(attrs={'size':5}),
      'ct_stem_practices': forms.SelectMultiple(attrs={'size':5}),
      'subject': forms.SelectMultiple(attrs={'size':4}),
    }

  def __init__(self, *args, **kwargs):
    super(LessonForm, self).__init__(*args, **kwargs)
    forms.ModelForm.__init__(self, *args, **kwargs)

    self.fields['ngss_standards'].label = "NGSS Standards"
    self.fields['ct_stem_practices'].label = "CT-STEM Practices"

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Lesson Activity Form
####################################
class LessonActivityForm(ModelForm):

  class Meta:
    model = models.LessonActivity
    exclude = ('order',)
    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'Activity Title'}),
      'content': forms.Textarea(attrs={'rows':0, 'cols':60}),
    }

  def __init__(self, *args, **kwargs):
    super(LessonActivityForm, self).__init__(*args, **kwargs)
    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Lesson Question Form
####################################
class LessonQuestionForm(ModelForm):

  class Meta:
    model = models.LessonQuestion
    exclude = ('order',)

####################################
#  Question Form
####################################
class QuestionForm(ModelForm):

  class Meta:
    model = models.Question
    fields = ['question_text', 'answer_field_type', 'options', 'answer']
    widgets = {
      'question_text': forms.TextInput(attrs={'placeholder': 'Enter question here'}),
      'options': forms.Textarea(attrs={'rows':5, 'cols':60, 'placeholder': 'Options for dropdown'}),
      'answer': forms.Textarea(attrs={'rows':5, 'cols':60, 'placeholder': 'Answer if applicable'}),
    }

  def __init__(self, *args, **kwargs):
    super(QuestionForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Assessment Form
####################################
class AssessmentForm(ModelForm):

  class Meta:
    model = models.Assessment
    fields = ['title', 'time', 'overview', 'status', 'subject', 'ngss_standards', 'ct_stem_practices']
    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'Lesson Title'}),
      'time': forms.TextInput(attrs={'rows':0, 'cols':60}),
      'overview': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'ngss_standards': forms.SelectMultiple(attrs={'size':5}),
      'ct_stem_practices': forms.SelectMultiple(attrs={'size':5}),
      'subject': forms.SelectMultiple(attrs={'size':4}),
    }

  def __init__(self, *args, **kwargs):
    super(AssessmentForm, self).__init__(*args, **kwargs)
    self.fields['ngss_standards'].label = "NGSS Standards"
    self.fields['ct_stem_practices'].label = "CT-STEM Practices"

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Assessment Form
####################################
class AssessmentStepForm(ModelForm):

  class Meta:
    model = models.AssessmentStep
    exclude = ('order',)
    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'Step Title'}),
      'content': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'teacher_notes': forms.Textarea(attrs={'rows':0, 'cols':60}),
    }

  def __init__(self, *args, **kwargs):
    super(AssessmentStepForm, self).__init__(*args, **kwargs)
    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text



class AssessmentQuestionForm(ModelForm):

  class Meta:
    model = models.AssessmentQuestion
    exclude = ('order',)

####################################
# NGSS Standards Form
####################################
class NGSSStandardForm(ModelForm):

  class Meta:
    model = models.NGSSStandard
    exclude = ('id',)
    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'NGSS Title'}),
      'description': forms.Textarea(attrs={'rows':0, 'cols':60}),
    }

  def __init__(self, *args, **kwargs):
    super(NGSSStandardForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# CTSTEM Practice Form
####################################
class CTStemPracticeForm(ModelForm):

  class Meta:
    model = models.CTStemPractice
    exclude = ('id',)
    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'CT-STEM Practice Title'}),
      'description': forms.Textarea(attrs={'rows':0, 'cols':60}),
    }

  def __init__(self, *args, **kwargs):
    super(CTStemPracticeForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Publication Form
####################################
class PublicationForm(ModelForm):

  class Meta:
    model = models.Publication
    exclude = ('created','slug')

  def __init__(self, *args, **kwargs):
    super(PublicationForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# User Group Form
####################################
class UserGroupForm(ModelForm):
  members = forms.ModelMultipleChoiceField(required=False, queryset=models.Student.objects.all(), widget=FilteredSelectMultiple(('Members'), False, attrs={'size':5}))

  class Meta:
    model = models.UserGroup
    exclude = ('id',)

  def __init__(self, *args, **kwargs):
    super(UserGroupForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

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

    self.save_m2m = save_m2m
    if commit:
        instance.save()
        self.save_m2m()

    return instance

####################################
# Assignment Form
####################################
class AssignmentForm(ModelForm):
  due_date = forms.DateField(widget=forms.DateInput(format='%b %d, %Y'), input_formats=['%b %d, %Y'])

  class Meta:
    model = models.Assignment
    exclude = ('group', )

  def __init__(self, *args, **kwargs):
    super(AssignmentForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
      if field_name == 'due_date':
        field.widget.attrs['class'] = 'form-control datepicker'
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
    uploadFile = forms.FileField()


####################################
# AssignmentStepResponse Form
####################################
class AssignmentStepResponseForm(ModelForm):
  class Meta:
    model = models.AssignmentStepResponse
    exclude = ('instance', 'assessment_step',)


####################################
# QuestionResponse Form
####################################
class QuestionResponseForm(ModelForm):
  class Meta:
    model = models.QuestionResponse
    exclude = ('created_date', 'modified_date',)

