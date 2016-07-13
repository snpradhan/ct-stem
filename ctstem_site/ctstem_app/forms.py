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
from datetime import datetime
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.widgets import RadioSelect, FileInput, ClearableFileInput
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist
from tinymce.widgets import TinyMCE
from django.db.models import Q

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

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(RegistrationForm, self).__init__(*args, **kwargs)
    if user.is_authenticated():
      if hasattr(user, 'school_administrator'):
        self.fields['account_type'].choices = models.USER_ROLE_CHOICES[4:]
        self.fields['school'].queryset = models.School.objects.filter(id=user.school_administrator.school.id)
      elif hasattr(user, 'teacher'):
        self.fields['account_type'].choices = models.USER_ROLE_CHOICES[5:]
        self.fields['school'].queryset = models.School.objects.filter(id=user.teacher.school.id)
    else:
      self.fields['account_type'].choices = models.USER_ROLE_CHOICES[3:]

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
    fields = ['curriculum_type', 'title', 'icon', 'time', 'level', 'purpose', 'overview', 'status', 'subject', 'taxonomy', 'content', 'teacher_notes']
    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'Lesson Title'}),
      'time': forms.TextInput(attrs={'rows':0, 'cols':60}),
      'level': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'purpose': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'overview': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'content': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'teacher_notes': forms.Textarea(attrs={'rows':0, 'cols':60}),
      'taxonomy': forms.SelectMultiple(attrs={'size':5}),
      'subject': forms.SelectMultiple(attrs={'size':4}),
    }

  def __init__(self, *args, **kwargs):
    super(CurriculumForm, self).__init__(*args, **kwargs)
    forms.ModelForm.__init__(self, *args, **kwargs)
    self.fields['taxonomy'].label = "Standards"

    for field_name, field in self.fields.items():
      field.widget.attrs['class'] = 'form-control'
      field.widget.attrs['placeholder'] = field.help_text

  def is_valid(self):
    valid = super(CurriculumForm, self).is_valid()
    if not valid:
      return valid

    if self.cleaned_data['curriculum_type'] == 'L' or self.cleaned_data['curriculum_type'] == 'A':
      if self.cleaned_data['title'] == '':
        self._errors['title'] = u'Title is required'
        valid = False
      if self.cleaned_data['time'] == '':
        self._errors['time'] = u'Time is required'
        valid = False
      if self.cleaned_data['level'] == '':
        self._errors['level'] = u'Level is required'
        valid = False
      if self.cleaned_data['purpose'] == '':
        self._errors['purpose'] = u'Purpose is required'
        valid = False
      if self.cleaned_data['overview'] == '':
        self._errors['overview'] = u'Overview is required'
        valid = False
      if not self.cleaned_data['taxonomy']:
          self._errors['taxonomy'] = u'Standards is required'
          valid = False

      if self.cleaned_data['curriculum_type'] == 'L':
        if not self.cleaned_data['subject']:
          self._errors['subject'] = u'Subject is required'
          valid = False
        if self.cleaned_data['content'] == '':
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
    fields = ['title', 'file_object']
    widgets = {
      'title': forms.TextInput(attrs={'placeholder': 'Activity Title'}),
      'file_object': widgets.NotClearableFileInput,
    }

  def __init__(self, *args, **kwargs):
    super(AttachmentForm, self).__init__(*args, **kwargs)
    for field_name, field in self.fields.items():
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
    self.fields["curriculum"].queryset = models.Curriculum.objects.filter(status='P')

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
# Curriculum Assignment Form
####################################
class CurriculumAssignmentForm(ModelForm):
  due_date = forms.DateField(widget=forms.DateInput(format='%b %d, %Y'), input_formats=['%b %d, %Y'])

  class Meta:
    model = models.Assignment
    exclude = ('curriculum', )

  def __init__(self, *args, **kwargs):
    super(CurriculumAssignmentForm, self).__init__(*args, **kwargs)

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
  uploadFile = forms.FileField(required=True)
  group = forms.ModelChoiceField(required=True, queryset=models.UserGroup.objects.all())

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(UploadFileForm, self).__init__(*args, **kwargs)
    print 'user', user
    if user.is_authenticated():
      if hasattr(user, 'school_administrator'):
        self.fields['group'].queryset = models.UserGroup.objects.all().filter(teacher__school=user.school_administrator.school)
      elif hasattr(user, 'teacher'):
        self.fields['group'].queryset = models.UserGroup.objects.all().filter(teacher=user.teacher)
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
    response = cleaned_data.get('response').strip()
    responseFile = cleaned_data.get('responseFile')
    save = cleaned_data.get('save')
    if save == False and not response and not responseFile:
      self.add_error('response', 'Please answer this question')
      self.add_error('responseFile', 'Please upload a file for this question')
    if responseFile and responseFile.size >  5*1024*1024:
      self.add_error('responseFile', 'Uploaded file cannot be bigger than 5MB')



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



