from django.db import models
from django.contrib.auth.models import User
from slugify import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField
from smart_selects.db_fields import ChainedForeignKey
from PIL import Image
import io
import datetime
import string
from django.utils.crypto import get_random_string
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import signals
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, m2m_changed, pre_delete
from django.db.models.functions import Upper
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.db.models import Func
import os


CURRICULUM_STATUS_CHOICES = (
    ('D', 'Private'),
    ('P', 'Public'),
    ('A', 'Archived'),
    ('R', 'Deleted'),
)

QUESTION_VISIBILITY_CHOICES = (
    ('D', 'Private'),
    ('P', 'Public'),
)

CURRICULUM_TYPE_CHOICES = (
    ('U', 'Unit'),
    ('L', 'Lesson'),
    ('A', 'Assessment'),
)
CURRICULUM_BUCKET_CHOICES = (
    (u'teacher_authored', u'Teacher Authored'),
    (u'my_curricula', u'My Curricula'),
    (u'shared_curricula', u'Shared Curricula'),
    (u'favorite_curricula', u'Favorite Curricula'),
)

CURRICULUM_PRIVILEGE_CHOICES = (
    ('V', 'View'),
    ('E', 'Edit'),
)

FIELD_TYPE_CHOICES = (
    ('TA', 'Text Area'),
    ('TF', 'Text Field'),
    ('DD', 'Drop Down'),
    ('MS', 'Multi-Select'),
    ('MC', 'Multiple Choice'),
    ('MI', 'Multiple Choice w/ Images'),
    ('MH', 'Multiple Choice w/ Horizontal Layout'),
    ('FI', 'File'),
    ('SK', 'Sketch'),
    ('DT', 'Data Table'),

)

USER_ROLE_CHOICES = (
    ('A', 'Site Administrator'),
    ('R', 'Researcher'),
    ('C', 'Content Author'),
    ('P', 'School Administrator'),
    ('T', 'Teacher'),
    ('S', 'Student'),
)

PUBLICATION_TYPES = (
  ('journal', 'Journal Articles'),
  ('book', 'Book Chapters'),
  ('refConfs', 'Refereed Conference Papers'),
  ('presentations', 'Presentations and Posters'),
  ('workshops', 'Workshop Papers'),
  ('others', 'Other Papers'),
)

ASSIGNMENT_STATUS = (
  ('N', 'New'),
  ('P', 'In Progress'),
  ('S', 'Submitted'),
  ('F', 'Feedback Completed'),
  ('A', 'Archived'),
)

ASSIGNMENT_SORT = (
  ('assigned', 'Assigned Date'),
  ('title', 'Assignment Title'),
  ('group', 'Class'),
  ('status', 'Assignment Status'),
  ('percent', 'Percent Complete'),
  ('modified', 'Last Modified')
)

PROGRESS_DASHBOARD_SORT = (
  ('student_id', 'Student ID'),
  ('student_last_first', 'Student Name (Last, First)'),
  ('student_first_last', 'Student Name (First, Last)'),
  ('most_progress', 'Most Progress'),
  ('least_progress', 'Least Progress'),
  ('most_time', 'Most Time Spent'),
  ('least_time', 'Least Time Spent'),
  ('newest_update', 'Most Recent Update'),
  ('oldest_update', 'Least Recent Update')
)
STUDENT_DASHBOARD_SORT = (
  ('student_id', 'Student ID'),
  ('student_last_first', 'Student Name (Last, First)'),
  ('student_first_last', 'Student Name (First, Last)'),
  ('most_recent_login', 'Most Recent Login'),
  ('least_recent_login', 'Least Recent Login'),
  ('most_progress', 'Most Progress'),
  ('least_progress', 'Least Progress'),
)

REQUESTER_ROLE = (
  ('', 'I am:'),
  ('T', 'Teacher'),
  ('R', 'Researcher'),
  ('A', 'School Administrator'),
  ('O', 'Other'),
)
CONSENT_CHOICES = (
  ('A', 'I Agree'),
  ('D', 'I Disagree'),
)
PARENTAL_CONSENT_CHOICES = (
  ('U', 'Unknown'),
  ('A', 'Agree'),
  ('D', 'Disagree'),
)

CURRICULA_SORT_CHOICES = (
  ('D', 'Date Updated'),
  ('A', 'Alphabetical'),
  ('P', 'Most Popular'),
)

CHANGE_TYPE_CHOICES = (
  ('A', 'Major Changes'),
  ('I', 'Minor Changes'),
  ('X', 'Bug Fixes'),
)

TOPIC_TYPE_CHOICES = (
  ('teacher_guide', 'Teacher Guide'),
  ('faq', 'Help and FAQ'),
)

PUBLICATION_TAG_CHOICES = (
  ('01', 'CT-Integration'),
  ('02', 'Teachers'),
  ('03', 'Students'),
  ('04', 'Methodology'),
)

class IsNull(Func):
  template = "%(expressions)s IS NULL or %(expressions)s = ''"

def upload_file_to(instance, filename):
  import os
  now = datetime.datetime.now()
  dt = now.strftime("%Y-%m-%d-%H-%M-%S-%f")
  filename_base, filename_ext = os.path.splitext(filename)
  print(filename, now, instance.id)
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
def generate_code_helper(length=5):
  allowed_chars = ''.join(('ABCDEFGHJKMNPQRSTUVWXYZ', '23456789'))
  code = get_random_string(length=length, allowed_chars=allowed_chars)
  schools = School.objects.all().filter(school_code=code)
  groups = UserGroup.objects.all().filter(group_code=code)
  curricula = Curriculum.objects.all().filter(curriculum_code=code)
  # ensure the user code is unique across teachers and researchers
  while schools.count() > 0 or groups.count() > 0 or curricula.count() > 0:
    code = get_random_string(length=length, allowed_chars=allowed_chars)
    schools = School.objects.all().filter(school_code=code)
    groups = UserGroup.objects.all().filter(group_code=code)
    curricula = Curriculum.objects.all().filter(curriculum_code=code)

  return code

# Create your models here.

class Curriculum (models.Model):
  curriculum_type = models.CharField(max_length=1, choices=CURRICULUM_TYPE_CHOICES)
  title = models.CharField(null=False, max_length=256, help_text='Name of Unit or Lesson')
  time = models.CharField(null=True, blank=True, max_length=256, help_text='Estimated time students would spend on this curriculum (ex. 7-9 class periods of 45-50 minutes)')
  level = models.TextField(null=True, blank=True, help_text="(ex. high school AP or Advanced Physics course)")
  purpose = RichTextUploadingField(null=True, blank=True, help_text="Purpose of this curriculum")
  overview = RichTextUploadingField(null=True, blank=True, help_text="Description of the curriculum")
  student_overview = RichTextUploadingField(null=True, blank=True, help_text="Description of what students will learn in this curriculum")
  content = RichTextUploadingField(null=True, blank=True)
  teacher_notes = RichTextUploadingField(null=True, blank=True)
  status = models.CharField(max_length=1, default='D', choices=CURRICULUM_STATUS_CHOICES)
  subject = models.ManyToManyField('Subject', blank=True, help_text="Select one or more subjects")
  compatible_system = models.ManyToManyField('System', blank=True, help_text="Select one or more compatible systems")
  parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
  version = models.IntegerField(default=1)
  taxonomy = models.ManyToManyField('Subcategory', blank=True)
  collaborators = models.ManyToManyField(to=User, through='CurriculumCollaborator', related_name='collaborated_curricula')
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)
  icon = models.ImageField(upload_to=upload_file_to, blank=True, null=True, help_text='Upload an image at least 400x289 in resolution that represents this curriculum')
  unit = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name="underlying_curriculum", help_text="Select a unit if this curriculum is part of one")
  acknowledgement = RichTextUploadingField(null=True, blank=True, help_text="Resources, models, and other material used in this curriculum; past authors/contributors")
  order = models.IntegerField(null=True, blank=True, help_text="Order within the Unit")
  credits = RichTextUploadingField(null=True, blank=True, help_text="Author contributions")
  feature_rank = models.IntegerField(null=True, blank=True, help_text="Order in the feature pool")
  curriculum_code = models.CharField(null=True, blank=True, max_length=30)

  class Meta:
      ordering = ['-id']

  def __str__(self):
      return '%s' % (self.title)

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

# CurriculumCollaborator through model
class CurriculumCollaborator(models.Model):
  curriculum = models.ForeignKey(Curriculum, null=False, on_delete=models.CASCADE)
  user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
  order = models.IntegerField(null=True, blank=True, help_text="Curriculum Order for Authors")
  privilege = models.CharField(max_length=1, choices=CURRICULUM_PRIVILEGE_CHOICES)

  class Meta:
      ordering = ['order']
      unique_together = ('curriculum', 'user')

# Curriculum Step model
# A curriculum may have one or more step/activity
class Step(models.Model):
  curriculum = models.ForeignKey(Curriculum, null=False, related_name="steps", on_delete=models.CASCADE)
  title = models.CharField(null=True, blank=True, max_length=256, help_text="Page title")
  order = models.IntegerField(null=True)
  content = RichTextUploadingField(null=True, blank=True)
  questions = models.ManyToManyField('Question', through='CurriculumQuestion', blank=True)

  class Meta:
      ordering = ['order']


# A relation between Curriculum and Question models
class CurriculumQuestion(models.Model):
  question = models.ForeignKey('Question', related_name="curriculum_question", on_delete=models.CASCADE)
  step = models.ForeignKey(Step, null=True, on_delete=models.CASCADE)
  order = models.IntegerField(null=True)
  referenced_by = models.CharField(null=True, blank=True, max_length=256)
  optional = models.BooleanField(default=False)

  def __str__(self):
      return '%s' % (self.question.question_text)

  class Meta:
      ordering = ['order']

# Lesson Attachment model
# A lesson may have one or more attachments
class Attachment(models.Model):
  curriculum = models.ForeignKey(Curriculum, null=False, on_delete=models.CASCADE)
  title = models.CharField(null=False, blank=False, max_length=256)
  file_object = models.FileField(upload_to=upload_file_to, null=False)
  teacher_only = models.BooleanField(choices=((False, 'No'), (True, 'Yes')), default=False)

  class Meta:
      ordering = ['title']

  def extension(self):
    name, extension = os.path.splitext(self.file_object.name)
    return extension

# Bookmarked Curriculum
class BookmarkedCurriculum(models.Model):
  curriculum = models.ForeignKey(Curriculum, null=False, related_name='bookmarked', on_delete=models.CASCADE)
  teacher = models.ForeignKey('Teacher', null=False, on_delete=models.CASCADE)
  created = models.DateTimeField(auto_now_add=True)

# Research Category
class ResearchCategory(models.Model):
  category = models.CharField(null=False, blank=False, max_length=256)
  description = models.TextField(null=True, blank=True)
  abbrevation = models.CharField(null=True, blank=True, max_length=10)
  flag = models.BooleanField(choices=((False, 'No'), (True, 'Yes')), default=False, help_text='Questions with category that are flagged will be identified as such.')

  def __str__(self):
    return '%s' % (self.category)

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
  research_category = models.ManyToManyField(ResearchCategory, blank=True, related_name='questions', help_text='On Windows use Ctrl+Click to make multiple selection.  On a Mac use Cmd+Click to make multiple selection')
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)
  visibility = models.CharField(max_length=1, default='D', choices=QUESTION_VISIBILITY_CHOICES)
  parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name="copied_questions")
  is_active = models.BooleanField(null=False, blank=False, default=True)

  def __str__(self):
      return '%s' % (self.question_text)

  def save(self, *args, **kwargs):
    if self.sketch_background:
      self.sketch_background = resizeImage(self.sketch_background, 900, 500)

    super(Question, self).save(*args, **kwargs)

  def get_flagged_categories(self):
    return self.research_category.all().filter(flag=True)

  def get_descendants_count(self):
    descendants = self.get_descendants()
    return len(descendants)

  def get_descendants(self):
    children = self.copied_questions.all()
    descendants = []
    if children:
      for child in children:
        descendants.append(child)
        descendants = descendants + child.get_descendants()

    return descendants

# Subject model
class Subject(models.Model):
  name = models.CharField(null=False, max_length=256)
  icon = models.ImageField(upload_to=upload_file_to, blank=True, null=True, help_text='Upload an image at least 400x289 in resolution that represents this subject')
  abbrevation = models.CharField(null=True, blank=True, max_length=10)

  def __str__(self):
      return '%s' % (self.name)

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

  def __str__(self):
      return '%s' % (self.name)

# Standards model
# These would include NGSS, CT-STEM Practice, Common Core, Illinois State Science Standards etc
class Standard(models.Model):
  name = models.CharField(null=False, max_length=256)
  short_name = models.CharField(null=False, max_length=256)
  primary = models.BooleanField(default=False)

  def __str__(self):
      return '%s' % (self.short_name)

# Category in a standard
class Category(models.Model):
  standard = models.ForeignKey(Standard, related_name="category", on_delete=models.CASCADE)
  name = models.CharField(null=False, max_length=256)
  icon = models.ImageField(upload_to=upload_file_to, blank=True, null=True, help_text='Upload an image at least 400x289 in resolution that represents this category')
  description = models.TextField(null=True, blank=True)
  order = models.IntegerField(null=True)

  def __str__(self):
      return '%s' % (self.name)

  class Meta:
      ordering = ['order']

  def save(self, *args, **kwargs):
    if self.icon:
      self.icon = resizeImage(self.icon, 400, 289)

    super(Category, self).save(*args, **kwargs)

# Subcategory model
class Subcategory(models.Model):
  category = models.ForeignKey(Category, related_name="subcategory", on_delete=models.CASCADE)
  title = models.CharField(null=False, max_length=512)
  code = models.CharField(null=True, max_length=256, blank=True)
  description = models.CharField(null=True, max_length=256, blank=True)
  link = models.URLField(null=True, max_length=500, blank=True)

  def __str__(self):
      return '%s' % (self.title)

  class Meta:
    ordering = ['code']

# School model
class School(models.Model):
  name = models.CharField(null=False, max_length=256)
  city = models.CharField(null=False, max_length=256)
  school_code = models.CharField(null=False, max_length=10, unique=True)
  is_active = models.BooleanField(null=False, blank=False, default=False)

  def __str__(self):
      return '%s' % (self.name)

###############################
# USER CLASSES
##############################
# Student model
class Student(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="student", on_delete=models.CASCADE)
  school = models.ForeignKey(School, null=True, on_delete=models.SET_NULL)
  consent = models.CharField(null=False, max_length=1, default='U', choices=CONSENT_CHOICES)
  parental_consent = models.CharField(null=False, max_length=1, default='U', choices=PARENTAL_CONSENT_CHOICES)
  test_account = models.BooleanField(null=False, blank=False, default=False)

  def __str__(self):
      return '%s, %s' % (self.user.last_name.title(), self.user.first_name.title())

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
  user = models.OneToOneField(User, unique=True, null=False, related_name="teacher", on_delete=models.CASCADE)
  school = models.ForeignKey(School, null=True, related_name="teachers", on_delete=models.SET_NULL)
  consent = models.CharField(null=False, max_length=1, default='U', choices=CONSENT_CHOICES)
  validation_code = models.CharField(null=False, max_length=5)

  class Meta:
      ordering = ['user__first_name', 'user__last_name']

  def __str__(self):
      return '%s' % (self.user.get_full_name())

# Researcher model
# This model represents researchers
class Researcher(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="researcher", on_delete=models.CASCADE)

  def __str__(self):
      return '%s' % (self.user.get_full_name())

# Administrator models
# This model represents a author user
class Author(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="author", on_delete=models.CASCADE)

  def __str__(self):
      return '%s' % (self.user.get_full_name())

# Administrator models
# This model represents a super user
class Administrator(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="administrator", on_delete=models.CASCADE)

  def __str__(self):
      return '%s' % (self.user.get_full_name())

# School Administrator model
# This model represents school administrators and school principals
class SchoolAdministrator(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="school_administrator", on_delete=models.CASCADE)
  school = models.ForeignKey(School, null=True, on_delete=models.SET_NULL)

  def __str__(self):
      return '%s' % (self.user.get_full_name())
#######################################################
# Publication model
#######################################################
class Publication(models.Model):
  description = RichTextField(null=False, blank=False, default="Enter publication", help_text="Enter publication details")
  tag = models.CharField(null=False, max_length=2, choices=PUBLICATION_TAG_CHOICES)
  authors = models.CharField(null=False, max_length=512, help_text="Enter comma separated list of authors: Last name, First initial.,")
  year = models.IntegerField(null=False)
  title = models.CharField(null=False, max_length=512)
  journal = models.CharField(null=False, max_length=512)
  volume = models.CharField(null=True, blank=True, max_length=50)
  issue = models.CharField(null=True, blank=True, max_length=50)
  from_page = models.CharField(null=True, blank=True, max_length=50)
  to_page = models.CharField(null=True, blank=True, max_length=50)
  web_link = models.URLField(null=True, blank=True, help_text="Start with http:// or https://")
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ['tag', 'year', 'authors']

#######################################################
# Group model
#######################################################
class UserGroup(models.Model):
  title = models.CharField(max_length=50, help_text='Class Title. Eg. Physics Section A')
  subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL)
  time = models.CharField(null=False, max_length=256)
  teacher = models.ForeignKey(Teacher, null=True, related_name='groups', on_delete=models.SET_NULL)
  description = models.TextField(null=True, blank=True)
  members = models.ManyToManyField(Student, through='Membership', blank=True, related_name='member_of')
  shared_with = models.ManyToManyField(Teacher, blank=True, related_name='shared_groups', help_text='Select teachers to share this class with.')
  group_code = models.CharField(null=False, blank=False, max_length=10, unique=True, default=generate_code_helper)
  is_active = models.BooleanField(null=False, blank=False, default=True)
  icon = models.ImageField(upload_to=upload_file_to, blank=True, null=True, help_text='Upload an image at least 400x289 in resolution that represents this class')
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

  def __str__(self):
    return '%s' % (self.title)

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
  curriculum = models.ForeignKey(Curriculum, related_name="assignments", on_delete=models.CASCADE)
  group = models.ForeignKey(UserGroup, related_name="assignments", on_delete=models.CASCADE)
  assigned_date = models.DateTimeField(auto_now_add=True)
  lock_on_completion = models.BooleanField(default=False)
  realtime_feedback = models.BooleanField(default=False)
  anonymize_student = models.BooleanField(default=False)

  def __str__(self):
    return '%s' % (self.curriculum.title)

  class Meta:
    unique_together = ('curriculum', 'group')

#######################################################
# Membership model
#######################################################
class Membership(models.Model):
  student = models.ForeignKey(Student, related_name="student_membership", on_delete=models.CASCADE)
  group = models.ForeignKey(UserGroup, related_name="group_members", on_delete=models.CASCADE)
  joined_on = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ('student__user__first_name', 'student__user__last_name')
#######################################################
# Assignment Instance Model
#######################################################
class AssignmentInstance(models.Model):
  assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
  student = models.ForeignKey(Student, related_name='instance', on_delete=models.CASCADE)
  teammates = models.ManyToManyField(Student, blank=True, help_text='On Windows use Ctrl+Click to make multiple selection.  On a Mac use Cmd+Click to make multiple selection')
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
  instance = models.OneToOneField(AssignmentInstance, unique=True, null=False, related_name="notes", on_delete=models.CASCADE)
  note = RichTextField(null=True, blank=True, config_name='student_response_ckeditor')

#######################################################
# Assignment Step Response Model
#######################################################
class AssignmentStepResponse(models.Model):
  instance = models.ForeignKey(AssignmentInstance, on_delete=models.CASCADE)
  step = models.ForeignKey(Step, on_delete=models.CASCADE)

  class Meta:
    unique_together = ('instance', 'step')

#######################################################
# Assignment Step Iframe State Model
# This model holds the state of each iframe embedded
# in a curriculum
#######################################################
class IframeState(models.Model):
  instance = models.ForeignKey(AssignmentInstance, on_delete=models.CASCADE)
  iframe_id = models.CharField(null=False, max_length=255)
  iframe_url = models.URLField(null=False, max_length=1600)
  state = models.TextField(null=True, blank=True)

  class Meta:
    unique_together = ('instance', 'iframe_id', 'iframe_url')

#######################################################
# Question Response Model
#######################################################
class QuestionResponse(models.Model):
  step_response = models.ForeignKey(AssignmentStepResponse, on_delete=models.CASCADE)
  curriculum_question = models.ForeignKey(CurriculumQuestion, on_delete=models.CASCADE)
  response = RichTextField(null=True, blank=True, config_name='student_response_ckeditor')
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = ('step_response', 'curriculum_question')


class QuestionResponseFile(models.Model):
  question_response = models.ForeignKey(QuestionResponse, related_name='response_file', null=False, on_delete=models.CASCADE)
  file = models.FileField(upload_to=upload_file_to, null=False, blank=False, help_text='Upload a file less than 5 MB in size.')

#######################################################
# Assignment Feedback Model
#######################################################
class AssignmentFeedback(models.Model):
  instance = models.ForeignKey(AssignmentInstance, unique=True, on_delete=models.CASCADE)

#######################################################
# Step Feedback Model
#######################################################
class StepFeedback(models.Model):
  assignment_feedback = models.ForeignKey(AssignmentFeedback, on_delete=models.CASCADE)
  step_response = models.ForeignKey(AssignmentStepResponse, on_delete=models.CASCADE)

  class Meta:
    ordering = ('step_response__step__order',)
    unique_together = ('assignment_feedback', 'step_response')

#######################################################
# Question Feedback Model
#######################################################
class QuestionFeedback(models.Model):
  step_feedback = models.ForeignKey(StepFeedback, on_delete=models.CASCADE)
  response = models.ForeignKey(QuestionResponse, on_delete=models.CASCADE)
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

  def __str__(self):
    return '%s' % (self.role)

  class Meta:
      ordering = ['order']

class Team(models.Model):
  role = models.ForeignKey(TeamRole, null=True, related_name='members', on_delete=models.SET_NULL)
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


class ReleaseNote(models.Model):
  version = models.CharField(max_length=255, blank=False, null=False, unique=True, help_text="Format: 3.2.1")
  release_date = models.DateField(blank=False, null=False)

  class Meta:
      ordering = ['-version']

class ReleaseChange(models.Model):
  release_note = models.ForeignKey(ReleaseNote, null=False, on_delete=models.CASCADE, related_name='changes')
  change_type = models.CharField(max_length=1, choices=CHANGE_TYPE_CHOICES)
  description = models.TextField(blank=False, null=False)

  class Meta:
      ordering = ['change_type']

class Topic(models.Model):
  name = models.CharField(max_length=512, blank=False)
  order = models.IntegerField(null=False, blank=False)
  topic_type = models.CharField(max_length=255, choices=TOPIC_TYPE_CHOICES)

  def __str__(self):
    return '%s' % (self.name)

  class Meta:
      ordering = ['order']

class SubTopic(models.Model):
  topic = models.ForeignKey(Topic, null=False, on_delete=models.CASCADE, related_name='subtopics')
  name = models.CharField(max_length=512, blank=False)
  order = models.IntegerField(blank=False, null=False)
  description = RichTextUploadingField(null=True, blank=True)
  modified_date = models.DateTimeField(auto_now=True)

  def __str__(self):
    return '%s' % (self.name)

  class Meta:
      ordering = ['order']

#signal used for is_active=False to is_active=True
@receiver(pre_save, sender=User, dispatch_uid='active')
def active(sender, instance, **kwargs):
  if instance.is_active and User.objects.filter(pk=instance.pk, is_active=False).exists():
    current_site = Site.objects.get_current()
    domain = current_site.domain
    body = '<div>Your account has been activated on Computational Thinking in STEM website https://%s.<div> \
            <div>You can login using the credentials created during registration.</div><br> \
            <div>If you have forgotten your password, you can reset them here https://%s/?next=/password_reset/recover/  </div><br> \
            <div><b>CT-STEM Admin</b></div>' % (domain, domain)

    send_mail('CT-STEM - Account Activated', body, settings.DEFAULT_FROM_EMAIL, [instance.email], html_message=body)

#signal to check if curriculum status has changed
@receiver(pre_save, sender=Curriculum)
def check_curriculum_status_change(sender, instance, **kwargs):
  try:
    obj = sender.objects.get(pk=instance.pk)
  except sender.DoesNotExist:
    pass # Object is new, so field hasn't technically changed, but you may want to do something else here.
  else:
    if not obj.status == instance.status: # status has changed
      # if changing the status of a unit, also update the status of underlying curricula
      if obj.curriculum_type == 'U':
        # if restoring a deleted Unit, also restore all underlying curricula
        if obj.status == 'R' and instance.status == 'A':
          Curriculum.objects.filter(unit=obj).update(status=instance.status)
        #otherwise only update the status of active (undeleted) underlying curricula
        else:
          Curriculum.objects.filter(unit=obj).exclude(status='R').update(status=instance.status)
          # if deleting a unit, also delete associated assignments
          if instance.status == 'R':
            Assignment.objects.filter(curriculum__unit__id=instance.id).delete()
      # if changing the status of an underlying curriculum to Public, also make Unit Public
      elif obj.unit and obj.unit.status != 'P' and instance.status == 'P':
        Curriculum.objects.filter(id=obj.unit.id).update(status='P')
      # if restoring an underlying curriculum in a deleted unit, also update the Unit status to Archived
      elif obj.unit and obj.unit.status == 'R' and instance.status == 'A':
        Curriculum.objects.filter(id=obj.unit.id).update(status='A')
      # if a curriculum is archived, also archive the associated assignments
      elif obj.status != 'R' and instance.status == 'A':
        AssignmentInstance.objects.filter(assignment__curriculum__id=instance.id).update(status= 'A')
      # if deleting a curriculum, also delete the associated assignments
      elif instance.status == 'R':
        Assignment.objects.filter(curriculum__id=instance.id).delete()

#signal to check if curriculum shared with has changed
@receiver(pre_save, sender=CurriculumCollaborator)
def check_curriculum_collaborators_change(sender, instance, **kwargs):

  '''action = kwargs.pop('action', None)
  pk_set = kwargs.pop('pk_set', None)
  instance = kwargs.pop('instance', None)
  '''
  try:
    obj = sender.objects.get(pk=instance.pk)
  except sender.DoesNotExist:
    # Object is new, so field hasn't technically changed, but you may want to do something else here.
    current_site = Site.objects.get_current()
    domain = current_site.domain
    body = subject = ''
    if instance.privilege == 'V':
      body =  '<div>A curriculum titled <b> %s </b> has been shared with you. </div><br> \
               <div>If you are logged in, you may click https://%s/curriculum/preview/%s/ to preview this curriculum. </div>\
               <div>If you are not logged in, you may click https://%s/?next=/login/?next=/curriculum/preview/%s/ to login and be redirected to the curriculum preview page.</div> \
               <div>You can also find this curriculum in your <b>Shared Curricula</b> collection on the Curricula page. </div><br><br> \
               <div><b>CT-STEM Admin</b></div>' % (instance.curriculum.title, domain, instance.curriculum.id, domain, instance.curriculum.id)
      subject = 'CT-STEM - Curriculum Shared'
    else:
      body =  '<div>You have been given edit privilege on a curriculum titled <b> %s</b>. </div><br> \
               <div>If you are logged in, you may click https://%s/curriculum/%s/overview/ to edit this curriculum.</div> \
               <div>If you are not logged in, you may click https://%s/?next=/login/?next=curriculum/%s/overview/ to login and be redirected to the curriculum edit page. </div> \
               <div>You can also find this curriculum in your <b>My Curricula</b> collection on the Curricula page. </div><br><br> \
               <div><b>CT-STEM Admin</b></div>' % (instance.curriculum.title, domain, instance.curriculum.id, domain, instance.curriculum.id)
      subject = 'CT-STEM - Curriculum Authoring Privilege'

    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [instance.user.email], html_message=body)

#m2m_changed.connect(check_curriculum_collaborators_change, sender=Curriculum.collaborators.through)

#signal to check if curriculum unit has changed
@receiver(pre_save, sender=Curriculum)
def check_curriculum_unit_change(sender, instance, **kwargs):
  try:
    obj = sender.objects.get(pk=instance.pk)
  except sender.DoesNotExist:
    pass # Object is new, so field hasn't technically changed, but you may want to do something else here.
  else:
    if obj.unit is None and instance.unit is not None: # stand alone unit added to a unit
      lesson_collaborators = CurriculumCollaborator.objects.all().filter(curriculum=obj).order_by('order')
      unit_author_count = CurriculumCollaborator.objects.all().filter(curriculum=instance.unit, privilege='E').count()

      for lesson_collaborator in lesson_collaborators:
        collaborator, created = CurriculumCollaborator.objects.get_or_create(curriculum=instance.unit, user=lesson_collaborator.user)

        if created:
          if lesson_collaborator.privilege == 'E':
            collaborator.privilege = 'E'
            unit_author_count = unit_author_count + 1
            collaborator.order = unit_author_count
          else:
            collaborator.privilege = 'V'
        elif lesson_collaborator.privilege == 'E' and collaborator.privilege != 'E':
          collaborator.privilege = 'E'
          unit_author_count = unit_author_count + 1
          collaborator.order = unit_author_count

        collaborator.save()
      lesson_collaborators.delete()


def resizeImage(img, minwidth, minheight):
  try:
    #check if the file actually exists
    image = Image.open(img)
    image = image.resize((minwidth, minheight), Image.ANTIALIAS)
    output = io.BytesIO()
    image.save(output, format='png', quality=75)
    output.seek(0)
    return InMemoryUploadedFile(output,'ImageField', "%s.png" %img.name, 'image/png', output.tell, None)
  except IOError as e:
    #file does not exists
    return None
