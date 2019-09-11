from django.db import models
from django.contrib.auth.models import User
from slugify import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField
from smart_selects.db_fields import ChainedForeignKey
from PIL import Image
import StringIO
import datetime
import string
from django.utils.crypto import get_random_string
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import signals
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.db.models.functions import Upper
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.db.models import Func


CURRICULUM_STATUS_CHOICES = (
    (u'D', u'Private'),
    (u'P', u'Public'),
    (u'A', u'Archived'),
)

CURRICULUM_TYPE_CHOICES = (
    (u'U', u'Unit'),
    (u'L', u'Lesson Plan'),
    (u'A', u'Assessment'),
    (u'S', u'Survey'),
)

FIELD_TYPE_CHOICES = (
    (u'TA', u'Text Area'),
    (u'TF', u'Text Field'),
    (u'DD', u'Drop Down'),
    (u'MS', u'Multi-Select'),
    (u'MC', u'Multiple Choice'),
    (u'MI', u'Multiple Choice w/ Images'),
    (u'MH', u'Multiple Choice w/ Horizontal Layout'),
    (u'FI', u'File'),
    (u'SK', u'Sketch'),
    (u'DT', u'Data Table'),

)

USER_ROLE_CHOICES = (
    (u'A', u'Site Administrator'),
    (u'R', u'Researcher'),
    (u'C', u'Content Author'),
    (u'P', u'School Administrator'),
    (u'T', u'Teacher'),
    (u'S', u'Student'),
)

PUBLICATION_TYPES = (
  (u'journal', u'Journal Articles'),
  (u'book', u'Book Chapters'),
  (u'refConfs', u'Refereed Conference Papers'),
  (u'presentations', u'Presentations and Posters'),
  (u'workshops', u'Workshop Papers'),
  (u'others', u'Other Papers'),
)

ASSIGNMENT_STATUS = (
  (u'N', u'New'),
  (u'P', u'In Progress'),
  (u'S', u'Submitted'),
  (u'F', u'Feedback Ready'),
  (u'A', u'Archived'),
)

ASSIGNMENT_SORT = (
  (u'assigned', u'Assigned Date'),
  (u'group', u'Group'),
  (u'due', u'Due Date'),
  (u'status', u'Status'),
  (u'percent', u'Percent Complete'),
  (u'modified', u'Last Modified')
)

REQUESTER_ROLE = (
  (u'', u'I am:'),
  (u'T', u'Teacher'),
  (u'R', u'Researcher'),
  (u'A', u'School Administrator'),
  (u'O', u'Other'),
)
CONSENT_CHOICES = (
  (u'A', u'I Agree'),
  (u'D', u'I Disagree'),
)
PARENTAL_CONSENT_CHOICES = (
  (u'U', u'Unknown'),
  (u'A', u'Agree'),
  (u'D', u'Disagree'),
)

class IsNull(Func):
  template = "%(expressions)s IS NULL or %(expressions)s = ''"

def upload_file_to(instance, filename):
  import os
  now = datetime.datetime.now()
  dt = now.strftime("%Y-%m-%d-%H-%M-%S-%f")
  filename_base, filename_ext = os.path.splitext(filename)
  print filename, now, instance.id
  if isinstance(instance, Curriculum):
    return 'curriculum/%s_%s%s' % (slugify(instance.title[:40]), dt, filename_ext.lower(),)
  elif isinstance(instance, Publication):
      return 'publications/%s_%s%s' % (slugify(instance.title[:40]), dt, filename_ext.lower(),)
  elif isinstance(instance, Subject):
      return 'subjects/%s_%s%s' % (slugify(instance.name[:40]), dt, filename_ext.lower(),)
  elif isinstance(instance, Team):
    return 'team/%s_%s%s' % (slugify(instance.name[:40]), dt, filename_ext.lower(),)
  elif isinstance(instance, Attachment):
    return 'attachment/%s_%s%s' % (slugify(filename_base.lower()[:40]), dt, filename_ext.lower(),)
  elif isinstance(instance, Category):
    return 'standard/%s_%s%s' % (slugify(filename_base.lower()[:40]), dt, filename_ext.lower(),)
  elif isinstance(instance, QuestionResponse):
    return 'questionResponse/%s/%s_%s%s' % (instance.step_response.instance.student.user.id, slugify(filename_base.lower()[:10]), dt, filename_ext.lower(),)
  elif isinstance(instance, Question):
    return 'question/%s_%s%s' % (slugify(filename_base.lower()[:40]), dt, filename_ext.lower(),)
  elif isinstance(instance, UserGroup):
    return 'group/%s_%s%s' % (slugify(filename_base.lower()[:40]), dt, filename_ext.lower(),)
  elif isinstance(instance, QuestionResponseFile):
    return 'questionResponse/%s/%s_%s%s' % (instance.question_response.step_response.instance.student.user.id, slugify(filename_base.lower()[:10]), dt, filename_ext.lower(),)

  return 'misc/%s_%s%s' % (filename_base.lower(), dt, filename_ext.lower(),)

####################################
# GENERATE UNIQUE USER CODE HELPER
####################################
def generate_code_helper():
  allowed_chars = ''.join(('ABCDEFGHJKMNPQRSTUVWXYZ', '23456789'))
  code = get_random_string(length=5, allowed_chars=allowed_chars)
  schools = School.objects.all().filter(school_code=code)
  groups = UserGroup.objects.all().filter(group_code=code)
  # ensure the user code is unique across teachers and researchers
  while schools.count() > 0 or groups.count() > 0:
    code = get_random_string(length=5, allowed_chars=allowed_chars)
    schools = School.objects.all().filter(school_code=code)
    groups = UserGroup.objects.all().filter(group_code=code)

  return code

# Create your models here.

class Curriculum (models.Model):
  curriculum_type = models.CharField(max_length=1, choices=CURRICULUM_TYPE_CHOICES)
  title = models.CharField(null=False, max_length=256, help_text='Name of Unit or Lesson')
  time = models.CharField(null=True, blank=True, max_length=256, help_text='Estimated time students would spend on this curriculum (ex. 7-9 class periods of 45-50 minutes)')
  level = models.TextField(null=True, blank=True, help_text="(ex. high school AP or Advanced Physics course)")
  purpose = RichTextUploadingField(null=True, blank=True, help_text="Purpose of this curriculum")
  overview = RichTextUploadingField(null=True, blank=True, help_text="Description of the curriculum; This text is shown to teachers and researchers only")
  student_overview = RichTextUploadingField(null=True, blank=True, help_text="Description of what students will learn in this curriculum; This text is shown to students only")
  content = RichTextUploadingField(null=True, blank=True)
  teacher_notes = RichTextUploadingField(null=True, blank=True)
  status = models.CharField(max_length=1, default='D', choices=CURRICULUM_STATUS_CHOICES)
  subject = models.ManyToManyField('Subject', null=True, blank=True, help_text="Select one or more subjects")
  compatible_system = models.ManyToManyField('System', null=True, blank=True, help_text="Select one or more compatible systems")
  parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
  version = models.IntegerField(default=1)
  taxonomy = models.ManyToManyField('Subcategory', null=True, blank=True)
  authors = models.ManyToManyField(User, null=False, related_name="curriculum_authors", help_text='Select authors for this curriculum')
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)
  icon = models.ImageField(upload_to=upload_file_to, blank=True, help_text='Upload an image at least 400x289 in resolution that represents this curriculum')
  shared_with = models.ManyToManyField('Teacher', null=True, blank=True, help_text='Select teachers to share this curriculum with before it is public' )
  unit = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name="underlying_curriculum", help_text="Select a unit if this curriculum is part of one")
  acknowledgement = RichTextUploadingField(null=True, blank=True, help_text="Resources, models, and other material used in this curriculum; past authors/contributors")
  order = models.IntegerField(null=True, blank=True, help_text="Order within the Unit")
  credits = RichTextUploadingField(null=True, blank=True, help_text="Author contributions")
  locked_by = models.ForeignKey(User, null=True)
  feature_rank = models.IntegerField(null=True, blank=True, help_text="Order in the feature pool")

  class Meta:
      ordering = ['-id']

  def __unicode__(self):
      return u'%s' % (self.title)

  def save(self, *args, **kwargs):
    if self.icon:
      self.icon = resizeImage(self.icon, 400, 289)

    super(Curriculum, self).save(*args, **kwargs)

  #get a list of direct ancestors
  def get_ancestors(self):
    if self.parent is None:
      return [self.id]
    else:
      return [self.id] + self.parent.get_ancestors()

  def usage_by_class(self):
    ancestors = self.get_ancestors()
    if self.curriculum_type == 'U':
      class_count = UserGroup.objects.all().filter(assignments__curriculum__unit__id__in=ancestors).distinct().count()
    else:
      class_count = UserGroup.objects.all().filter(assignments__curriculum__id__in=ancestors).distinct().count()
    return class_count

  def usage_by_teacher(self):
    ancestors = self.get_ancestors()
    if self.curriculum_type == 'U':
      teacher_count = Teacher.objects.all().filter(groups__assignments__curriculum__unit__id__in=ancestors).distinct().count()
    else:
      teacher_count = Teacher.objects.all().filter(groups__assignments__curriculum__id__in=ancestors).distinct().count()
    return teacher_count

  def usage_by_school(self):
    ancestors = self.get_ancestors()
    if self.curriculum_type == 'U':
      school_count = School.objects.all().filter(teachers__groups__assignments__curriculum__unit__id__in=ancestors).distinct().count()
    else:
      school_count = School.objects.all().filter(teachers__groups__assignments__curriculum__id__in=ancestors).distinct().count()
    return school_count

  def usage_by_student(self):
    ancestors = self.get_ancestors()
    if self.curriculum_type == 'U':
      student_count = Student.objects.all().filter(member_of__assignments__curriculum__unit__id__in=ancestors).distinct().count()
    else:
      student_count = Student.objects.all().filter(member_of__assignments__curriculum__id__in=ancestors).distinct().count()
    return student_count

# Curriculum Step model
# A curriculum may have one or more step/activity
class Step(models.Model):
  curriculum = models.ForeignKey(Curriculum, null=False, related_name="steps")
  title = models.CharField(null=True, blank=True, max_length=256, help_text="Page title")
  order = models.IntegerField(null=True)
  content = RichTextUploadingField(null=True, blank=True)
  teacher_notes = RichTextUploadingField(null=True, blank=True)
  questions = models.ManyToManyField('Question', through='CurriculumQuestion', blank=True)

  class Meta:
      ordering = ['order']


# A relation between Curriculum and Question models
class CurriculumQuestion(models.Model):
  question = models.ForeignKey('Question', related_name="curriculum_question")
  step = models.ForeignKey(Step, null=True)
  order = models.IntegerField(null=True)
  referenced_by = models.CharField(null=True, blank=True, max_length=256)
  optional = models.BooleanField(default=False)

  def __unicode__(self):
      return u'%s' % (self.question.question_text)

  class Meta:
      ordering = ['order']

# Lesson Attachment model
# A lesson may have one or more attachments
class Attachment(models.Model):
  curriculum = models.ForeignKey(Curriculum, null=False)
  title = models.CharField(null=False, blank=False, max_length=256)
  file_object = models.FileField(upload_to=upload_file_to, null=False)
  teacher_only = models.BooleanField(choices=((True, 'Yes'), (False, 'No')))


  class Meta:
      ordering = ['title']


# Bookmarked Curriculum
class BookmarkedCurriculum(models.Model):
  curriculum = models.ForeignKey(Curriculum, null=False, related_name='bookmarked')
  teacher = models.ForeignKey('Teacher', null=False)
  created = models.DateTimeField(auto_now_add=True)

# Research Category
class ResearchCategory(models.Model):
  category = models.CharField(null=False, blank=False, max_length=256)
  description = models.TextField(null=True, blank=True)

  def __unicode__(self):
    return u'%s' % (self.category)

  class Meta:
    ordering = ['category']

  def save(self, *args, **kwargs):
    if self.description is None or self.description == '':
      self.description = self.category
    super(ResearchCategory, self).save(*args, **kwargs)

# Question model
# A bank of questions that can be resued across assessments and lessons
class Question(models.Model):
  question_text = RichTextUploadingField(null=False, blank=False, config_name='question_ckeditor')
  answer_field_type = models.CharField(null=False, max_length=2, choices=FIELD_TYPE_CHOICES, default='TF')
  options = models.TextField(null=True, blank=True, help_text="Click on the &#9432; icon to see the Options Guide")
  display_other_option = models.BooleanField(null=False, blank=False, default=False)
  answer = models.TextField(null=True, blank=True)
  sketch_background = models.ImageField(upload_to=upload_file_to, blank=True, null=True, help_text='Upload a background image at least 900x500 in resolution for the sketch pad')
  research_category = models.ManyToManyField(ResearchCategory, null=True, blank=True, related_name='questions')

  def __unicode__(self):
      return u'%s' % (self.question_text)

  def save(self, *args, **kwargs):
    if self.sketch_background:
      self.sketch_background = resizeImage(self.sketch_background, 900, 500)

    super(Question, self).save(*args, **kwargs)

# Subject model
class Subject(models.Model):
  name = models.CharField(null=False, max_length=256)
  abbrevation = models.CharField(null=True, blank=True, max_length=10)
  icon = models.ImageField(upload_to=upload_file_to, blank=True, help_text='Upload an image at least 400x289 in resolution that represents this subject')

  def __unicode__(self):
      return u'%s' % (self.name)

  class Meta:
    ordering = ['name']

  def save(self, *args, **kwargs):
    if self.icon:
      self.icon = resizeImage(self.icon, 400, 289)
    super(Subject, self).save(*args, **kwargs)

# Compatible devices and OS
class System(models.Model):
  name = models.CharField(null=False, max_length=256)
  icon = models.CharField(null=False, max_length=256)

  def __unicode__(self):
      return u'%s' % (self.name)

# Standards model
# These would include NGSS, CT-STEM Practice, Common Core, Illinois State Science Standards etc
class Standard(models.Model):
  name = models.CharField(null=False, max_length=256)
  short_name = models.CharField(null=False, max_length=256)
  primary = models.BooleanField(default=False)

  def __unicode__(self):
      return u'%s' % (self.short_name)

# Category in a standard
class Category(models.Model):
  standard = models.ForeignKey(Standard, related_name="category")
  name = models.CharField(null=False, max_length=256)
  icon = models.ImageField(upload_to=upload_file_to, blank=True, null=True, help_text='Upload an image at least 400x289 in resolution that represents this category')
  description = models.TextField(null=True, blank=True)
  order = models.IntegerField(null=True)

  def __unicode__(self):
      return u'%s' % (self.name)

  class Meta:
      ordering = ['order']

  def save(self, *args, **kwargs):
    if self.icon:
      self.icon = resizeImage(self.icon, 400, 289)

    super(Category, self).save(*args, **kwargs)

# Subcategory model
class Subcategory(models.Model):
  category = models.ForeignKey(Category, related_name="subcategory")
  title = models.CharField(null=False, max_length=512)
  code = models.CharField(null=True, max_length=256, blank=True)
  description = models.CharField(null=True, max_length=256, blank=True)
  link = models.URLField(null=True, max_length=500, blank=True)

  def __unicode__(self):
      return u'%s' % (self.title)

  class Meta:
    ordering = ['code']

# School model
class School(models.Model):
  name = models.CharField(null=False, max_length=256)
  city = models.CharField(null=False, max_length=256)
  school_code = models.CharField(null=False, max_length=10, unique=True)
  is_active = models.BooleanField(null=False, blank=False, default=False)

  def __unicode__(self):
      return u'%s' % (self.name)

###############################
# USER CLASSES
##############################
# Student model
class Student(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="student")
  school = models.ForeignKey(School)
  consent = models.CharField(null=False, max_length=1, default='U', choices=CONSENT_CHOICES)
  parental_consent = models.CharField(null=False, max_length=1, default='U', choices=PARENTAL_CONSENT_CHOICES)

  def __unicode__(self):
      return u'%s, %s' % (self.user.last_name, self.user.first_name)

  def get_consent(self):
    if self.consent == 'A':
      return 'Agree'
    elif self.consent == 'D':
      return 'Disagree'
    else:
      return 'Unknown'

  def get_parental_consent(self):
    if self.parental_consent == 'A':
      return 'Agree'
    elif self.parental_consent == 'D':
      return 'Disagree'
    else:
      return 'Unknown'

# Teacher models
# This is a user class model
class Teacher(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="teacher")
  school = models.ForeignKey(School, related_name="teachers")
  consent = models.CharField(null=False, max_length=1, default='U', choices=CONSENT_CHOICES)
  validation_code = models.CharField(null=False, max_length=5)

  class Meta:
      ordering = ['user__first_name', 'user__last_name']

  def __unicode__(self):
      return u'%s' % (self.user.get_full_name())

# Researcher model
# This model represents researchers
class Researcher(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="researcher")

  def __unicode__(self):
      return u'%s' % (self.user.get_full_name())

# Administrator models
# This model represents a author user
class Author(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="author")

  def __unicode__(self):
      return u'%s' % (self.user.get_full_name())

# Administrator models
# This model represents a super user
class Administrator(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="administrator")

  def __unicode__(self):
      return u'%s' % (self.user.get_full_name())

# School Administrator model
# This model represents school administrators and school principals
class SchoolAdministrator(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="school_administrator")
  school = models.ForeignKey(School)

  def __unicode__(self):
      return u'%s' % (self.user.get_full_name())
#######################################################
# Publication model
#######################################################
class Publication(models.Model):
  authors = models.CharField(max_length=255, help_text='Publication Author')
  year = models.CharField(max_length=255, help_text='Publication Year')
  title = models.CharField(max_length=255, help_text='Publication Title')
  journal = models.CharField(max_length=255)
  pages = models.CharField(max_length=255, blank=True)
  award = models.CharField(max_length=255, blank=True)
  slug = models.SlugField(unique=True, max_length=255)
  created = models.DateTimeField(auto_now_add=True)
  local_copy = models.FileField(upload_to=upload_file_to, blank=True)
  web_link = models.URLField(blank=True)
  publication_type = models.CharField(max_length=255, choices=PUBLICATION_TYPES)

#######################################################
# Group model
#######################################################
class UserGroup(models.Model):
  title = models.CharField(max_length=50, help_text='Class Title. Eg. Physics Section A')
  subject = models.ForeignKey(Subject, null=True, blank=True)
  time = models.CharField(null=False, max_length=256)
  teacher = models.ForeignKey(Teacher, related_name='groups')
  description = models.TextField(null=True, blank=True)
  members = models.ManyToManyField(Student, through='Membership', blank=True, null=True, related_name='member_of')
  shared_with = models.ManyToManyField(Teacher, null=True, blank=True, help_text='Select teachers to share this class with.' )
  group_code = models.CharField(null=False, blank=False, max_length=10, unique=True, default=generate_code_helper)
  is_active = models.BooleanField(null=False, blank=False, default=True)
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)
  icon = models.ImageField(upload_to=upload_file_to, blank=True, help_text='Upload an image at least 400x289 in resolution that represents this class')

  def __unicode__(self):
    return u'%s' % (self.title)

  class Meta:
    ordering = ['title']

  def save(self, *args, **kwargs):
    if self.icon:
      self.icon = resizeImage(self.icon, 400, 289)

    super(UserGroup, self).save(*args, **kwargs)


#######################################################
# Assignment model
#######################################################
class Assignment(models.Model):
  curriculum = models.ForeignKey(Curriculum, related_name="assignments")
  group = models.ForeignKey(UserGroup, related_name="assignments")
  assigned_date = models.DateTimeField(auto_now_add=True)
  lock_on_completion = models.BooleanField(default=False)

  def __unicode__(self):
    return u'%s' % (self.curriculum.title)

#######################################################
# Membership model
#######################################################
class Membership(models.Model):
  student = models.ForeignKey(Student, related_name="student_membership")
  group = models.ForeignKey(UserGroup, related_name="group_members")
  joined_on = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ('student__user__first_name', 'student__user__last_name')
#######################################################
# Assignment Instance Model
#######################################################
class AssignmentInstance(models.Model):
  assignment = models.ForeignKey(Assignment)
  student = models.ForeignKey(Student, related_name='instance')
  teammates = models.ManyToManyField(Student, blank=True, null=True, help_text='On Windows use Ctrl+Click to make multiple selection.  On a Mac use Cmd+Click to make multiple selection')
  status = models.CharField(max_length=255, choices=ASSIGNMENT_STATUS, default='N')
  last_step = models.IntegerField(null=False, blank=False, default=0)
  time_spent = models.FloatField(null=False, blank=False, default=0.0)
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = ('assignment', 'student')

#######################################################
# Assignment Notes Model
#######################################################
class AssignmentNotes(models.Model):
  instance = models.OneToOneField(AssignmentInstance, unique=True, null=False, related_name="notes")
  note = RichTextField(null=True, blank=True, config_name='student_response_ckeditor')

#######################################################
# Assignment Step Response Model
#######################################################
class AssignmentStepResponse(models.Model):
  instance = models.ForeignKey(AssignmentInstance)
  step = models.ForeignKey(Step)

  class Meta:
    unique_together = ('instance', 'step')

#######################################################
# Assignment Step Iframe State Model
# This model holds the state of each iframe embedded
# in a curriculum
#######################################################
class IframeState(models.Model):
  instance = models.ForeignKey(AssignmentInstance)
  iframe_id = models.CharField(null=False, max_length=255)
  iframe_url = models.URLField(null=False, max_length=1600)
  state = models.TextField(null=True, blank=True)

  class Meta:
    unique_together = ('instance', 'iframe_id', 'iframe_url')

#######################################################
# Question Response Model
#######################################################
class QuestionResponse(models.Model):
  step_response = models.ForeignKey(AssignmentStepResponse)
  curriculum_question = models.ForeignKey(CurriculumQuestion)
  response = RichTextField(null=True, blank=True, config_name='student_response_ckeditor')
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = ('step_response', 'curriculum_question')


class QuestionResponseFile(models.Model):
  question_response = models.ForeignKey(QuestionResponse, related_name='response_file', null=False)
  file = models.FileField(upload_to=upload_file_to, null=False, blank=False, help_text='Upload a file less than 5 MB in size.')

#######################################################
# Assignment Feedback Model
#######################################################
class AssignmentFeedback(models.Model):
  instance = models.ForeignKey(AssignmentInstance)

#######################################################
# Step Feedback Model
#######################################################
class StepFeedback(models.Model):
  assignment_feedback = models.ForeignKey(AssignmentFeedback)
  step_response = models.ForeignKey(AssignmentStepResponse)

  class Meta:
    ordering = ('step_response__step__order',)
    unique_together = ('assignment_feedback', 'step_response')

#######################################################
# Question Feedback Model
#######################################################
class QuestionFeedback(models.Model):
  step_feedback = models.ForeignKey(StepFeedback)
  response = models.ForeignKey(QuestionResponse)
  feedback = models.TextField(null=True, blank=True, help_text="Enter Feedback")
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ('response__curriculum_question__order',)
    unique_together = ('step_feedback', 'response')

#######################################################
# Team Model
#######################################################
class TeamRole(models.Model):
  role = models.CharField(max_length=255, blank=False)
  order = models.IntegerField(null=False, blank=False, unique=True)

  def __unicode__(self):
    return u'%s' % (self.role)

  class Meta:
      ordering = ['order']

class Team(models.Model):
  role = models.ForeignKey(TeamRole, related_name='members')
  current = models.BooleanField(default=True)
  name = models.CharField(max_length=255, blank=False)
  description = models.TextField(null=True)
  url = models.URLField(null=True, max_length=500, blank=True)
  image = models.ImageField(upload_to=upload_file_to, blank=False)
  order = models.IntegerField(null=False, blank=False)

  class Meta:
      ordering = ['order']

class TrainingRequest(models.Model):
  name = models.CharField(max_length=255, blank=False, null=False, help_text="Name")
  email = models.EmailField(max_length=255, blank=False, null=False, help_text="Email")
  school = models.CharField(max_length=255, blank=False, null=False, help_text="School Name")
  subject = models.CharField(max_length=255, blank=False, null=False, help_text="Subject")
  created_date = models.DateTimeField(auto_now_add=True)


#signal used for is_active=False to is_active=True
@receiver(pre_save, sender=User, dispatch_uid='active')
def active(sender, instance, **kwargs):
  if instance.is_active and User.objects.filter(pk=instance.pk, is_active=False).exists():
    current_site = Site.objects.get_current()
    domain = current_site.domain
    body = '<div>Your account has been activated on Computational Thinking in STEM website http://%s.<div> \
            <div>You can login using the credentials created during registration.</div><br> \
            <div>If you have forgotten your password, you can reset them here http://%s/password_reset/recover/  </div><br> \
            <div><b>CT-STEM Admin</b></div>' % (domain, domain)

    send_mail('CT-STEM - Account Activated', body, settings.DEFAULT_FROM_EMAIL, [instance.email], html_message=body)

def resizeImage(img, minwidth, minheight):
  try:
    #check if the file actually exists
    img.read()
    img.seek(0)
    image = Image.open(StringIO.StringIO(img.read()))
    image = image.resize((minwidth, minheight), Image.ANTIALIAS)
    output = StringIO.StringIO()
    image.save(output, format='png', quality=75)
    output.seek(0)
    return InMemoryUploadedFile(output,'ImageField', "%s.png" %img.name, 'image/png', output.len, None)
  except IOError, e:
    #file does not exists
    return None
