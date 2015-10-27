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
    super(RegistrationForm, self).__init__(*args, **kwargs)
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
    #check password
    if self.cleaned_data['password1'] != self.cleaned_data['password2']:
      self._errors['password1'] = u'Passwords are not identical'
      clean = False
    #check school
    if self.cleaned_data['account_type'] in ['S', 'T', 'R']:
      if self.cleaned_data['school'] is None or self.cleaned_data['school'] == '':
        self._errors['school'] = u'School is required'
        clean =  False

    # check permission code
    if self.cleaned_data['account_type'] in ['S', 'T']:
      if self.cleaned_data['permission_code'] is None or self.cleaned_data['permission_code'] == '':
        self._errors['permission_code'] = u'Permission code is required'
        clean = False
      elif self.cleaned_data['account_type'] == 'T':
        try:
          models.Researcher.objects.get(permission_code=self.cleaned_data['permission_code'])
        except models.Researcher.DoesNotExist:
          self._errors['permission_code'] = u'Permission code is not valid'
          clean = False
      elif self.cleaned_data['account_type'] == 'S':
        try:
          models.Teacher.objects.get(permission_code=self.cleaned_data['permission_code'])
        except models.Teacher.DoesNotExist:
          self._errors['permission_code'] = u'Permission code is not valid'
          clean = False

    return clean

####################################
# UserProfile Form
####################################
class UserProfileForm(ModelForm):
  password1 = forms.CharField(widget=forms.PasswordInput, required=False, label=u'Password', help_text="Leave this field blank to retain old password")
  password2 = forms.CharField(widget=forms.PasswordInput, required=False, label=u'Confirm Password')

  class Meta:
    model = models.User
    fields = ["username","first_name", "last_name", "email", "password1", "password2"]

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
    fields = ['school','students', 'permission_code']

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
    fields = ['school','teachers', 'permission_code']
  def __init__(self, *args, **kwargs):
    super(ResearcherForm, self).__init__(*args, **kwargs)
    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Lesson Form
####################################
class LessonForm(ModelForm):
  questions = forms.ModelMultipleChoiceField(required=False, queryset=models.Question.objects.all(), widget=FilteredSelectMultiple(('Questions'), False, attrs={'size':15}))

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
    if self.instance.id:
      if 'instance' in kwargs:
        initial = kwargs.setdefault('initial', {})
        initial['questions'] = [t.pk for t in kwargs['instance'].questions.all()]
    forms.ModelForm.__init__(self, *args, **kwargs)
    if 'instance' in kwargs:
      self.fields['questions'].queryset = models.Question.objects.all()

    self.fields['ngss_standards'].label = "NGSS Standards"
    self.fields['ct_stem_practices'].label = "CT-STEM Practices"

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

  def save(self, commit=True):
    instance = forms.ModelForm.save(self, False)
    old_save_m2m = self.save_m2m

    def save_m2m():
      old_save_m2m()
      old_questions = models.LessonQuestion.objects.filter(lesson=instance)
      for old_question in old_questions:
        changed = True
        for curr_question in self.cleaned_data['questions']:
          if old_question.question == curr_question:
            changed = False
        if changed:
          old_question.delete()

      for question in self.cleaned_data['questions']:
        try:
          models.LessonQuestion.objects.get(lesson=instance, question=question)
        except models.LessonQuestion.DoesNotExist:
          q = models.LessonQuestion(lesson=instance, question=question)
          q.save()

    self.save_m2m = save_m2m
    if commit:
      instance.save()
      self.save_m2m()
    return instance

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

  '''def save(self, commit=True):
    instance = forms.ModelForm.save(self, False)
    old_save_m2m = self.save_m2m

    def save_m2m():

      old_save_m2m()
      old_questions = models.AssessmentQuestion.objects.filter(assessment_step=instance)
      for old_question in old_questions:
        changed = True
        for curr_question in self.cleaned_data['assessmentquestion_set']:
          if old_question.question == curr_question:
            changed = False
        if changed:
          old_question.delete()

      for question in self.cleaned_data['assessmentquestion_set']:
        try:
          models.AssessmentQuestion.objects.get(assessment_step=instance, question=question)
        except models.AssessmentQuestion.DoesNotExist:
          q = models.AssessmentQuestion(assessment_step=instance, question=question)
          q.save()

    self.save_m2m = save_m2m
    if commit:
      instance.save()
      self.save_m2m()
    return instance'''

class AssessmentQuestionForm(ModelForm):

  class Meta:
    model = models.AssessmentQuestion
    exclude = ('order',)
