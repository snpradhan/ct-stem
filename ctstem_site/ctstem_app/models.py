from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from slugify import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from smart_selects.db_fields import ChainedForeignKey
from PIL import Image
import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile


CURRICULUM_STATUS_CHOICES = (
    (u'D', u'Draft'),
    (u'P', u'Published'),
    (u'A', u'Archived'),
)

CURRICULUM_TYPE_CHOICES = (
    (u'L', u'Lesson Plan'),
    (u'A', u'Assessment'),
)

FIELD_TYPE_CHOICES = (
    (u'TA', u'Text Area'),
    (u'TF', u'Text Field'),
    (u'DD', u'Drop Down'),
    (u'MS', u'Multi-Select'),
    (u'MC', u'Multiple Choice'),
    (u'FI', u'File'),
)

USER_ROLE_CHOICES = (
    (u'A', u'Site Administrator'),
    (u'R', u'Researcher/School Admin'),
    (u'C', u'Content Author'),
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

def upload_file_to(instance, filename):
  import os
  from django.utils.timezone import now
  filename_base, filename_ext = os.path.splitext(filename)
  print filename
  if isinstance(instance, Curriculum):
    return 'curriculum/%s%s' % (slugify(instance.title), filename_ext.lower(),)
  elif isinstance(instance, Publication):
      return 'publications/%s%s' % (slugify(instance.title), filename_ext.lower(),)
  elif isinstance(instance, Team):
    return 'team/%s%s' % (slugify(instance.name), filename_ext.lower(),)
  elif isinstance(instance, Attachment):
    return 'attachment/%s%s' % (filename_base.lower(), filename_ext.lower(),)
  elif isinstance(instance, Category):
    return 'standard/%s%s' % (filename_base.lower(), filename_ext.lower(),)
  elif isinstance(instance, QuestionResponse):
    return 'questionResponse/%s/%s%s' % (instance.step_response.instance.student.user, filename_base.lower(), filename_ext.lower(),)
  return 'misc/%s%s' % (instance.id,filename_ext.lower(),)

# Create your models here.

class Curriculum (models.Model):
  curriculum_type = models.CharField(max_length=1, choices=CURRICULUM_TYPE_CHOICES)
  title = models.CharField(null=False, max_length=256)
  time = models.CharField(null=True, max_length=256)
  level = models.TextField(null=False)
  purpose = models.TextField(null=False)
  overview = models.TextField(null=False)
  content = RichTextUploadingField(null=False)
  teacher_notes = RichTextUploadingField(null=True, blank=True)
  status = models.CharField(max_length=1, default='D', choices=CURRICULUM_STATUS_CHOICES)
  subject = models.ManyToManyField('Subject', null=False)
  parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)
  version = models.IntegerField(default=1)
  slug = models.SlugField(unique=True, max_length=255)
  taxonomy = models.ManyToManyField('Subcategory')
  author = models.ForeignKey(User, null=False, related_name='curriculum_author')
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)
  icon = models.ImageField(upload_to=upload_file_to, blank=True)

  class Meta:
      ordering = ['-id']

  def __unicode__(self):
      return u'%s' % (self.title)

  def save(self, *args, **kwargs):
    if self.icon:
      image = Image.open(StringIO.StringIO(self.icon.read()))
      image = image.resize((400,289), Image.ANTIALIAS)
      output = StringIO.StringIO()
      image.save(output, format='png', quality=75)
      output.seek(0)
      self.icon = InMemoryUploadedFile(output,'ImageField', "%s.png" %self.icon.name, 'image/png', output.len, None)

    super(Curriculum, self).save(*args, **kwargs)

# Curriculum Step model
# A curriculum may have one or more step/activity
class Step(models.Model):
  curriculum = models.ForeignKey(Curriculum, null=False, related_name="steps")
  title = models.CharField(null=False, blank=False, max_length=256)
  order = models.IntegerField(null=True)
  content = RichTextUploadingField(null=False)
  teacher_notes = RichTextUploadingField(null=True, blank=True)
  questions = models.ManyToManyField('Question', through='CurriculumQuestion', blank=True)

  class Meta:
      ordering = ['order']


# A relation between Curriculum and Question models
class CurriculumQuestion(models.Model):
  question = models.ForeignKey('Question', related_name="curriculum_question")
  step = models.ForeignKey(Step, null=True)
  order = models.IntegerField(null=True)

  def __unicode__(self):
      return u'%s' % (self.question.question_text)

  class Meta:
      ordering = ['order']

# Lesson Attachment model
# A lesson may have one or more attachments
class Attachment(models.Model):
  curriculum = models.ForeignKey(Curriculum, null=False)
  title = models.CharField(null=False, blank=False, max_length=256)
  file_object = models.FileField(upload_to=upload_file_to, blank=True)

  class Meta:
      ordering = ['title']


# Bookmarked Curriculum
class BookmarkedCurriculum(models.Model):
  curriculum = models.ForeignKey(Curriculum, null=False, related_name='bookmarked')
  teacher = models.ForeignKey('Teacher', null=False)
  created = models.DateTimeField(auto_now_add=True)

# Question model
# A bank of questions that can be resued across assessments and lessons
class Question(models.Model):
  question_text = RichTextUploadingField(null=False, blank=False, config_name='question_ckeditor')
  answer_field_type = models.CharField(null=False, max_length=2, choices=FIELD_TYPE_CHOICES)
  options = models.TextField(null=True, blank=True)
  answer = models.TextField(null=True, blank=True)

  def __unicode__(self):
      return u'%s' % (self.question_text)

# Subject model
class Subject(models.Model):
  name = models.CharField(null=False, max_length=256)
  abbrevation = models.CharField(null=True, blank=True, max_length=10)

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
  icon = models.ImageField(upload_to=upload_file_to, blank=True, null=True)
  order = models.IntegerField(null=True)

  def __unicode__(self):
      return u'%s' % (self.name)

  class Meta:
      ordering = ['order']

  def save(self, *args, **kwargs):
    if self.icon:
      image = Image.open(StringIO.StringIO(self.icon.read()))
      image = image.resize((400,289), Image.ANTIALIAS)
      output = StringIO.StringIO()
      image.save(output, format='png', quality=75)
      output.seek(0)
      self.icon = InMemoryUploadedFile(output,'ImageField', "%s.png" %self.icon.name, 'image/png', output.len, None)

    super(Category, self).save(*args, **kwargs)

# Subcategory model
class Subcategory(models.Model):
  category = models.ForeignKey(Category, related_name="subcategory")
  title = models.CharField(null=False, max_length=256)
  code = models.CharField(null=True, max_length=256, blank=True)
  description = models.CharField(null=True, max_length=256, blank=True)
  link = models.URLField(null=True, max_length=500, blank=True)

  def __unicode__(self):
      return u'%s' % (self.title)

# School model
class School(models.Model):
  name = models.CharField(null=False, max_length=256)
  city = models.CharField(null=False, max_length=256)
  school_code = models.CharField(null=False, max_length=10, unique=True)

  def __unicode__(self):
      return u'%s' % (self.name)

###############################
# USER CLASSES
##############################
# Student model
class Student(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="student")
  school = models.ForeignKey(School)

  def __unicode__(self):
      return u'%s' % (self.user.get_full_name())

# Teacher models
# This is a user class model
class Teacher(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="teacher")
  school = models.ForeignKey(School)
  students = models.ManyToManyField(Student, blank=True)
  user_code = models.CharField(null=False, max_length=256, unique=True)

  def __unicode__(self):
      return u'%s' % (self.user.get_full_name())

# Researcher model
# This model represents researchers, school admins and school principals
class Researcher(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="researcher")
  school = models.ForeignKey(School)
  teachers = models.ManyToManyField(Teacher, blank=True)
  user_code = models.CharField(null=False, max_length=256, unique=True)

  def __unicode__(self):
      return u'%s' % (self.user.get_full_name())

# Administrator models
# This model represents a super user
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

######################################################
# Section models
# This models represents a class, group or a section of a teacher that has one or more students
class Section(models.Model):
  teacher = models.ForeignKey(Teacher)
  subject = models.ForeignKey(Subject)
  time = models.CharField(null=False, max_length=256)
  students = models.ManyToManyField(Student)


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
  title = models.CharField(max_length=255, help_text='Group Title. Eg. Physics Section A')
  subject = models.ForeignKey(Subject)
  time = models.CharField(null=False, max_length=256)
  teacher = models.ForeignKey(Teacher, related_name='groups')
  description = models.TextField(null=True)
  members = models.ManyToManyField(Student, through='Membership', blank=True, null=True, related_name='member_of')

  def __unicode__(self):
    return u'%s' % (self.title)

#######################################################
# Assignment model
#######################################################
class Assignment(models.Model):
  curriculum = models.ForeignKey(Curriculum)
  group = models.ForeignKey(UserGroup, related_name="assignments")
  assigned_date = models.DateTimeField(auto_now_add=True)
  due_date = models.DateTimeField(null=False, blank=False)

  def __unicode__(self):
    return u'%s' % (self.curriculum.title)

#######################################################
# Membership model
#######################################################
class Membership(models.Model):
  student = models.ForeignKey(Student)
  group = models.ForeignKey(UserGroup, related_name="group_members")
  joined_on = models.DateTimeField(auto_now_add=True)


#######################################################
# Assignment Instance Model
#######################################################
class AssignmentInstance(models.Model):
  assignment = models.ForeignKey(Assignment)
  student = models.ForeignKey(Student)
  status = models.CharField(max_length=255, choices=ASSIGNMENT_STATUS)
  last_step = models.IntegerField(null=False, blank=False, default=0)
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = ('assignment', 'student')


#######################################################
# Assignment Step Response Model
#######################################################
class AssignmentStepResponse(models.Model):
  instance = models.ForeignKey(AssignmentInstance)
  step = models.ForeignKey(Step)

  class Meta:
    unique_together = ('instance', 'step')

#######################################################
# Question Response Model
#######################################################
class QuestionResponse(models.Model):
  step_response = models.ForeignKey(AssignmentStepResponse)
  curriculum_question = models.ForeignKey(CurriculumQuestion)
  response = models.TextField(null=True, blank=True)
  responseFile = models.FileField(upload_to=upload_file_to, blank=True)
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = ('step_response', 'curriculum_question')

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

#######################################################
# Question Feedback Model
#######################################################
class QuestionFeedback(models.Model):
  step_feedback = models.ForeignKey(StepFeedback)
  response = models.ForeignKey(QuestionResponse)
  feedback = models.TextField(null=True, blank=True, help_text="Enter Feedback")
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)


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
  name = models.CharField(max_length=255, blank=False)
  description = models.TextField(null=True)
  url = models.URLField(null=True, max_length=500, blank=True)
  image = models.ImageField(upload_to=upload_file_to, blank=False)
  order = models.IntegerField(null=False, blank=False)

  class Meta:
      ordering = ['order']
