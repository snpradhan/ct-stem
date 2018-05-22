from django import forms
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from ctstem_app import models, widgets
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
from django.core.exceptions import ObjectDoesNotExist
from tinymce.widgets import TinyMCE
from django.db.models import Q
import os

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
  school = forms.ModelChoiceField(required=False, queryset=models.School.objects.all().filter(is_active=True).order_by('name'))

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    group_id = None
    if 'group_id' in kwargs:
      group_id = kwargs.pop('group_id')
    super(RegistrationForm, self).__init__(*args, **kwargs)
    if user.is_authenticated():
      if hasattr(user, 'school_administrator'):
        self.fields['account_type'].choices = models.USER_ROLE_CHOICES[4:]
        self.fields['school'].queryset = models.School.objects.filter(id=user.school_administrator.school.id)
      elif hasattr(user, 'teacher'):
        self.fields['account_type'].choices = models.USER_ROLE_CHOICES[5:]
        self.fields['school'].queryset = models.School.objects.filter(id=user.teacher.school.id)
      elif hasattr(user, 'administrator'):
        self.fields['school'].queryset = models.School.objects.filter(~Q(school_code='OTHER'), is_active=True)

    elif group_id:
      self.fields['account_type'].choices = models.USER_ROLE_CHOICES[3:]
      self.fields['email'].widget.attrs['readonly'] = True
    else:
      self.fields['account_type'].choices = models.USER_ROLE_CHOICES[4:5]

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text


  def clean_username(self):
    if User.objects.filter(username=self.cleaned_data['username'].lower()).count() > 0:
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
    #check fields for Teacher, Student and School Administrator
    if self.cleaned_data['account_type'] in ['T', 'S', 'P']:
      if self.cleaned_data['school'] is None or self.cleaned_data['school'] == '':
        error_list.append('SR');

    if len(error_list) > 0:
      clean = False

    for error in error_list:
      if error == 'SR':
        self._errors['school'] = u'School is required'


    return clean

####################################
# Validation Form
####################################
class ValidationForm (forms.Form):
  username = forms.RegexField(required=True, regex=r'^\w+$', max_length=30, label=u'Username')
  password = forms.CharField(required=True, widget=forms.PasswordInput(render_value=False), label=u'Password')
  validation_code = forms.CharField(required=True, label=u'Validation Code')

  def __init__(self, *args, **kwargs):
    super(ValidationForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['aria-describedby'] = field.label
      field.widget.attrs['placeholder'] = field.help_text

  def is_valid(self):
    valid = super(ValidationForm, self).is_valid()
    if not valid:
      return valid

    username = self.cleaned_data['username'].lower()
    password = self.cleaned_data['password']
    validation_code = self.cleaned_data['validation_code']
    try:
      user = User.objects.get(username=username)
      teacher = models.Teacher.objects.get(user=user)
    except (User.DoesNotExist, models.Teacher.DoesNotExist):
      self.errors['username'] = u'Username is invalid'
      return False

    if not user.check_password(password):
      self.errors['password'] = u'Password is invalid'
      return False

    if teacher.validation_code != validation_code:
      self.errors['validation_code'] = u'Validation Code is invalid'
      return False

    return True

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
    fields = ['school', 'consent', 'parental_consent']
    widgets = {
      'consent': forms.RadioSelect()
    }

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(StudentForm, self).__init__(*args, **kwargs)
    if user.is_authenticated():
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
        self.fields['school'].queryset = models.School.objects.filter(~Q(school_code='OTHER'), is_active=True)

      if hasattr(user, 'student') == False:
        del self.fields['consent']
      if hasattr(user, 'administrator') == False:
        del self.fields['parental_consent']

    for field_name, field in self.fields.items():
      if field_name != 'consent':
        field.widget.attrs['class'] = 'form-control'
        field.widget.attrs['aria-describedby'] = field.label
        field.widget.attrs['placeholder'] = field.help_text
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

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(TeacherForm, self).__init__(*args, **kwargs)

    if user.is_authenticated():
      if hasattr(user, 'school_administrator'):
        school = user.school_administrator.school
      elif hasattr(user, 'teacher'):
        school = user.teacher.school
      else:
        school = None

      if school is not None:
        self.fields['school'].queryset = models.School.objects.filter(id=school.id)
      else:
        self.fields['school'].queryset = models.School.objects.filter(~Q(school_code='OTHER'), is_active=True)

    else:
      self.fields['school'].queryset = models.School.objects.all().filter(is_active=True)

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
    fields = []
  def __init__(self, *args, **kwargs):
    super(ResearcherForm, self).__init__(*args, **kwargs)
    for field_name, field in self.fields.items():
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
    if user.is_authenticated() and hasattr(user, 'school_administrator'):
      school = user.school_administrator.school
      self.fields['school'].queryset = models.School.objects.filter(id=school.id)
    else:
      self.fields['school'].queryset = models.School.objects.filter(~Q(school_code='OTHER'), is_active=True)

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
# Curriculum Form
####################################
class CurriculumForm(ModelForm):

  class Meta:
    model = models.Curriculum
    fields = ['curriculum_type', 'unit', 'authors', 'order', 'title', 'icon', 'time', 'level', 'purpose', 'overview', 'student_overview', 'acknowledgement', 'credits', 'status', 'subject', 'compatible_system', 'taxonomy', 'content', 'teacher_notes', 'shared_with']

    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'Lesson Title'}),
      'time': forms.TextInput(attrs={'rows':0, 'cols':60}),
      'level': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'purpose': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'overview': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'student_overview': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'content': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'teacher_notes': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'taxonomy': forms.SelectMultiple(attrs={'size':5}),
      'authors': forms.SelectMultiple(attrs={'size':5}),
      'subject': forms.SelectMultiple(attrs={'size':4}),
      'compatible_system': forms.SelectMultiple(attrs={'size':6}),
      'shared_with': forms.SelectMultiple(attrs={'size':10}),
      'acknowledgement': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'credits': forms.Textarea(attrs={'rows':0, 'cols':60}),
    }

  def __init__(self, *args, **kwargs):
    super(CurriculumForm, self).__init__(*args, **kwargs)
    forms.ModelForm.__init__(self, *args, **kwargs)
    self.fields['taxonomy'].label = "Standards"
    self.fields['order'].label = "Lesson Order"
    self.fields['authors'].choices = [(user.pk, user.get_full_name()) for user in models.User.objects.all().filter(Q(administrator__isnull=False) | Q(researcher__isnull=False) | Q(author__isnull=False)).order_by('first_name', 'last_name')]
    self.fields['unit'].queryset = models.Curriculum.objects.filter(curriculum_type='U')

    if self.instance.id:
      self.fields['curriculum_type'].widget.attrs['disabled'] = True

    for field_name, field in self.fields.items():
      if field_name == 'order':
        field.widget.attrs['class'] = 'form-control order'
      else:
        field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

  def is_valid(self):
    valid = super(CurriculumForm, self).is_valid()
    if not valid:
      return valid

    cleaned_data = super(CurriculumForm, self).clean()

    if cleaned_data.get('curriculum_type') == 'U'  or cleaned_data.get('curriculum_type') == 'L' or cleaned_data.get('curriculum_type') == 'A':
      if cleaned_data.get('icon'):
        try:
          cleaned_data.get('icon').read()
        except IOError, e:
          self._errors['icon'] = u'Icon file is invalid. Please upload a new icon.'
          valid = False
      if cleaned_data.get('title') == '':
        self._errors['title'] = u'Title is required'
        valid = False
      if cleaned_data.get('time') == '':
        self._errors['time'] = u'Time is required'
        valid = False
      if cleaned_data.get('curriculum_type') != 'L' or not cleaned_data.get('unit'):
        if cleaned_data.get('level') == '':
          self._errors['level'] = u'Level is required'
          valid = False
        if cleaned_data.get('purpose') == '':
          self._errors['purpose'] = u'Purpose is required'
          valid = False
        if cleaned_data.get('overview') == '':
          self._errors['overview'] = u'Overview is required'
          valid = False
      if not cleaned_data.get('taxonomy') and not cleaned_data.get('unit'):
          self._errors['taxonomy'] = u'Standards is required'
          valid = False

      if cleaned_data.get('curriculum_type') == 'U'  or cleaned_data.get('curriculum_type') == 'L':
        if cleaned_data.get('curriculum_type') != 'L' or not cleaned_data.get('unit'):
          if not cleaned_data.get('subject'):
            self._errors['subject'] = u'Subject is required'
            valid = False
          if cleaned_data.get('content') == '':
            self._errors['content'] = u'Content is required'
            valid = False
    return valid

####################################
# Curriculum Step Form
####################################
class StepForm(ModelForm):

  class Meta:
    model = models.Step
    exclude = ('order',)
    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'Step Title'}),
      'content': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'teacher_notes': forms.Textarea(attrs={'rows':0, 'cols':60}),
    }

  def __init__(self, *args, **kwargs):
    super(StepForm, self).__init__(*args, **kwargs)
    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text


####################################
# Lesson Attachment Form
####################################
class AttachmentForm(ModelForm):

  class Meta:
    model = models.Attachment
    fields = ['title', 'file_object', 'teacher_only']
    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'Activity Title'}),
      'file_object': widgets.NotClearableFileInput,
      'teacher_only': forms.Select(),
    }

  def __init__(self, *args, **kwargs):
    super(AttachmentForm, self).__init__(*args, **kwargs)
    for field_name, field in self.fields.items():
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
      except IOError, e:
        self._errors['file_object'] = u'Attached file is invalid. Please upload a new attachment.'
        valid = False

    return valid

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
    fields = ['research_category', 'question_text', 'answer_field_type', 'sketch_background', 'options', 'answer']
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
#  Research Category Form
####################################
class ResearchCategoryForm(ModelForm):

  class Meta:
    model = models.ResearchCategory
    fields = ['category', 'description']
    widgets = {
      'category': forms.TextInput(attrs={'placeholder': 'Enter category here'}),
      'description': forms.Textarea(attrs={'rows':5, 'cols':60, 'placeholder': 'Category description'}),
    }

  def __init__(self, *args, **kwargs):
    super(ResearchCategoryForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

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

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text

####################################
# Taxonomy Search Form
####################################
class TaxonomySearchForm(ModelForm):
  standard = forms.ModelChoiceField(queryset=models.Standard.objects.all())

  class Meta:
    model = models.Subcategory
    exclude = ('id', 'description', 'link',)
    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'Standards title'}),
      'code': forms.TextInput(attrs={'placeholder': 'Standards code'}),
    }

  def __init__(self, *args, **kwargs):
    super(TaxonomySearchForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text

      if field_name == 'category':
        field.queryset = models.Category.objects.none()

####################################
# Student Search Form
####################################
class StudentSearchForm(forms.Form):
  username = forms.CharField(required=False, max_length=30, label=u'Username')
  first_name = forms.CharField(required=False, max_length=30, label=u'First name')
  last_name = forms.CharField(required=False, max_length=30, label=u'Last name')
  email = forms.EmailField(required=False, max_length=75, label=u'Email')

  def __init__(self, *args, **kwargs):
    super(StudentSearchForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text

####################################
# Teacher Search Form
####################################
class TeacherSearchForm(forms.Form):
  username = forms.CharField(required=False, max_length=30, label=u'Username')
  first_name = forms.CharField(required=False, max_length=30, label=u'First name')
  last_name = forms.CharField(required=False, max_length=30, label=u'Last name')
  email = forms.EmailField(required=False, max_length=75, label=u'Email')

  def __init__(self, *args, **kwargs):
    super(TeacherSearchForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text
####################################
# Create and Add Student Form
####################################
class StudentAddForm(forms.Form):

  username = forms.RegexField(required=True, regex=r'^\w+$', max_length=30, label=u'Username',
                              error_messages={'invalid': 'Usernames may only contain letters, numbers, and underscores (_)'})
  first_name = forms.CharField(required=True, max_length=30, label=u'First name')
  last_name = forms.CharField(required=True, max_length=30, label=u'Last name')
  email = forms.EmailField(required=True, max_length=75, label=u'Email')

  def __init__(self, *args, **kwargs):
    super(StudentAddForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      if field.required:
        field.widget.attrs['required'] = 'required'
      if field.help_text:
        field.widget.attrs['placeholder'] = field.help_text

####################################
# Assignment Search Form
####################################
class AssignmentSearchForm(forms.Form):
  curriculum_type = forms.ChoiceField(choices=models.CURRICULUM_TYPE_CHOICES)
  title = forms.CharField(max_length=256)
  subject = forms.ModelChoiceField(queryset=models.Subject.objects.all())

  def __init__(self, *args, **kwargs):
    super(AssignmentSearchForm, self).__init__(*args, **kwargs)

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

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Category Form
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
  #members = forms.ModelMultipleChoiceField(required=False, queryset=models.Student.objects.all(), widget=FilteredSelectMultiple(('Members'), False, attrs={'size':5}))

  class Meta:
    model = models.UserGroup
    exclude = ('id',)

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(UserGroupForm, self).__init__(*args, **kwargs)

    self.fields['time'].label = 'Time/Period'
    if hasattr(user, 'teacher'):
      self.fields['members'].queryset = self.fields['members'].queryset.filter(school=user.teacher.school)
    elif hasattr(user, 'school_administrator'):
      self.fields['teacher'].queryset = self.fields['teacher'].queryset.filter(school=user.school_administrator.school)
      self.fields['members'].queryset = self.fields['members'].queryset.filter(school=user.school_administrator.school)

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

    #if group is inactive, disable all fields
    if self.instance.is_active == False:
      for field_name, field in self.fields.items():
        field.widget.attrs['disabled'] = True

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
  assigned_date = forms.DateField(widget=forms.DateInput(format='%b %d, %Y'), input_formats=['%b %d, %Y'])

  class Meta:
    model = models.Assignment
    exclude = ('group', )
    #fields = ['id', 'curriculum', 'group', 'assigned_date', 'due_date']

  def __init__(self, *args, **kwargs):
    super(AssignmentForm, self).__init__(*args, **kwargs)
    self.fields["curriculum"].queryset = models.Curriculum.objects.filter(status='P')

    for field_name, field in self.fields.items():
      if field_name == 'due_date':
        if self.instance.id == None:
          field.widget.attrs['class'] = 'form-control datepicker due'
        elif self.instance.id and self.instance.group.is_active:
          field.widget.attrs['class'] = 'form-control datepicker due'
        else:
          field.widget.attrs['class'] = 'form-control'
        field.widget.attrs['readonly'] = True
      elif field_name =='assigned_date':
        if self.instance.id and self.instance.assigned_date.date() <= date.today():
          field.widget.attrs['class'] = 'form-control'
        else:
          field.widget.attrs['class'] = 'form-control datepicker assigned'
        field.widget.attrs['readonly'] = True
      else:
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

    for field_name, field in self.fields.items():
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
    print 'user', user
    if user.is_authenticated():
      if hasattr(user, 'school_administrator'):
        self.fields['group'].queryset = models.UserGroup.objects.all().filter(teacher__school=user.school_administrator.school, is_active=True)
      elif hasattr(user, 'teacher'):
        self.fields['group'].queryset = models.UserGroup.objects.all().filter(teacher=user.teacher, is_active=True)
    else:
      self.fields['group'].queryset = models.UserGroup.objects.none()

    for field_name, field in self.fields.items():
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

    for field_name, field in self.fields.items():
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
    for field_name, field in self.fields.items():
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
    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

  def clean(self):
    cleaned_data = super(QuestionResponseFileForm, self).clean()
    file = cleaned_data.get('file')
    delete = cleaned_data.get('DELETE')
    if not delete and file.size > 5*1024*1024:
      self.add_error('file', 'Uploaded file cannot be bigger than 5MB')

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

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Assignment Sort Form
####################################
class InboxSortForm (forms.Form):
  sort_by = forms.ChoiceField(required=False, choices = models.ASSIGNMENT_SORT)

  def __init__(self, *args, **kwargs):
    super(InboxSortForm, self).__init__(*args, **kwargs)
    self.initial['sort_by'] = 'A'

    for field_name, field in self.fields.items():
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

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

      if field_name == 'name':
        field.label = 'School Name'

####################################
# Subject Form
####################################
class SubjectForm(ModelForm):

  class Meta:
    model = models.Subject
    exclude = ('id',)

  def __init__(self, *args, **kwargs):
    super(SubjectForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Team Role Form
####################################
class TeamRoleForm(ModelForm):

  class Meta:
    model = models.TeamRole
    exclude = ('id', 'order',)

  def __init__(self, *args, **kwargs):
    super(TeamRoleForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

####################################
# Team Member Form
####################################
class TeamMemberForm(ModelForm):

  class Meta:
    model = models.Team
    exclude = ('id',)

  def __init__(self, *args, **kwargs):
    super(TeamMemberForm, self).__init__(*args, **kwargs)

    for field_name, field in self.fields.items():
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

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

  def is_valid(self):
    valid = super(TrainingRequestForm, self).is_valid()
    return valid

