from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from slugify import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField
from smart_selects.db_fields import ChainedForeignKey
from PIL import Image
import StringIO
import datetime
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import signals
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site


CURRICULUM_STATUS_CHOICES = (
    (u'D', u'Draft'),
    (u'P', u'Published'),
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

def upload_file_to(instance, filename):
  import os
  now = datetime.datetime.now()
  dt = now.strftime("%Y-%m-%d-%H-%M-%S-%f")
  filename_base, filename_ext = os.path.splitext(filename)
  print filename, now
  if isinstance(instance, Curriculum):
    return 'curriculum/%s_%s%s' % (slugify(instance.title[:40]), dt, filename_ext.lower(),)
  elif isinstance(instance, Publication):
      return 'publications/%s_%s%s' % (slugify(instance.title[:40]), dt, filename_ext.lower(),)
  elif isinstance(instance, Team):
    return 'team/%s_%s%s' % (slugify(instance.name[:40]), dt, filename_ext.lower(),)
  elif isinstance(instance, Attachment):
    return 'attachment/%s_%s%s' % (slugify(filename_base.lower()[:40]), dt, filename_ext.lower(),)
  elif isinstance(instance, Category):
    return 'standard/%s_%s%s' % (slugify(filename_base.lower()[:40]), dt, filename_ext.lower(),)
  elif isinstance(instance, QuestionResponse):
    return 'questionResponse/%s/%s_%s%s' % (instance.step_response.instance.student.user, slugify(filename_base.lower()[:10]), dt, filename_ext.lower(),)
  elif isinstance(instance, Question):
    return 'question/%s_%s%s' % (slugify(filename_base.lower()[:40]), dt, filename_ext.lower(),)
  elif isinstance(instance, QuestionResponseFile):
    return 'questionResponse/%s/%s_%s%s' % (instance.question_response.step_response.instance.student.user, slugify(filename_base.lower()[:10]), dt, filename_ext.lower(),)

  return 'misc/%s_%s%s' % (filename_base.lower(), dt, filename_ext.lower(),)

# Create your models here.

class Curriculum (models.Model):
  curriculum_type = models.CharField(max_length=1, choices=CURRICULUM_TYPE_CHOICES)
  title = models.CharField(null=False, max_length=256, help_text='Curriculum title')
  time = models.CharField(null=True, blank=True, max_length=256, help_text='Estimated time students would spend on this curriculum')
  level = RichTextUploadingField(null=True, blank=True, help_text="Student level")
  purpose = RichTextUploadingField(null=True, blank=True, help_text="Purpose of this curriculum")
  overview = RichTextUploadingField(null=True, blank=True, help_text="Curriculum overview for teachers")
  student_overview = RichTextUploadingField(null=True, blank=True, help_text="Curriculum overview for students")
  content = RichTextUploadingField(null=True, blank=True)
  teacher_notes = RichTextUploadingField(null=True, blank=True)
  status = models.CharField(max_length=1, default='D', choices=CURRICULUM_STATUS_CHOICES)
  subject = models.ManyToManyField('Subject', null=True, blank=True, help_text="Select one or more subjects")
  compatible_system = models.ManyToManyField('System', null=True, blank=True, help_text="Select one or more compatible systems")
  parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
  version = models.IntegerField(default=1)
  slug = models.SlugField(unique=True, max_length=255)
  taxonomy = models.ManyToManyField('Subcategory', null=True, blank=True)
  author = models.ForeignKey(User, null=False, related_name='curriculum_author')
  authors = models.ManyToManyField(User, null=False, related_name="curriculum_authors")
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)
  icon = models.ImageField(upload_to=upload_file_to, blank=True, help_text='Upload 400x289 png image that represents this curriculum')
  shared_with = models.ManyToManyField('Teacher', null=True, blank=True, help_text='Select teachers to share this curriculum with before it is published.' )
  unit = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name="underlying_curriculum", help_text="Select a unit if this lesson is part of one")
  acknowledgement = RichTextUploadingField(null=True, blank=True)
  order = models.IntegerField(null=True, blank=True)

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
  title = models.CharField(null=True, blank=True, max_length=256, help_text="Step title")
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

# Question model
# A bank of questions that can be resued across assessments and lessons
class Question(models.Model):
  question_text = RichTextUploadingField(null=False, blank=False, config_name='question_ckeditor')
  answer_field_type = models.CharField(null=False, max_length=2, choices=FIELD_TYPE_CHOICES, default='TF')
  options = models.TextField(null=True, blank=True, help_text="For dropdown, multi-select and multiple choice questions provide one option per line. For multiple choice w/ images provide one image url per line. For a data table, provide one table header per line")
  answer = models.TextField(null=True, blank=True)
  sketch_background = models.ImageField(upload_to=upload_file_to, blank=True, null=True)
  research_category = models.ForeignKey(ResearchCategory, null=True, blank=True, related_name='questions', on_delete=models.SET_NULL)

  def __unicode__(self):
      return u'%s' % (self.question_text)

# Subject model
class Subject(models.Model):
  name = models.CharField(null=False, max_length=256)
  abbrevation = models.CharField(null=True, blank=True, max_length=10)

  def __unicode__(self):
      return u'%s' % (self.name)

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
  icon = models.ImageField(upload_to=upload_file_to, blank=True, null=True)
  description = models.TextField(null=True, blank=True)
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
      return u'%s' % (self.user.get_full_name())

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
  school = models.ForeignKey(School)
  consent = models.CharField(null=False, max_length=1, default='U', choices=CONSENT_CHOICES)
  validation_code = models.CharField(null=False, max_length=5)

  def __unicode__(self):
      return u'%s' % (self.user.get_full_name())

# Researcher model
# This model represents researchers
class Researcher(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="researcher")

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
  title = models.CharField(max_length=255, help_text='Group Title. Eg. Physics Section A')
  subject = models.ForeignKey(Subject)
  time = models.CharField(null=False, max_length=256)
  teacher = models.ForeignKey(Teacher, related_name='groups')
  description = models.TextField(null=True)
  members = models.ManyToManyField(Student, through='Membership', blank=True, null=True, related_name='member_of')
  is_active = models.BooleanField(null=False, blank=False, default=True)

  def __unicode__(self):
    return u'%s' % (self.title)

#######################################################
# Assignment model
#######################################################
class Assignment(models.Model):
  curriculum = models.ForeignKey(Curriculum, related_name="assignments")
  group = models.ForeignKey(UserGroup, related_name="assignments")
  assigned_date = models.DateTimeField(default=datetime.datetime.now, blank=False)
  due_date = models.DateTimeField(null=False, blank=False)

  def __unicode__(self):
    return u'%s' % (self.curriculum.title)

#######################################################
# Membership model
#######################################################
class Membership(models.Model):
  student = models.ForeignKey(Student, related_name="student_membership")
  group = models.ForeignKey(UserGroup, related_name="group_members")
  joined_on = models.DateTimeField(auto_now_add=True)


#######################################################
# Assignment Instance Model
#######################################################
class AssignmentInstance(models.Model):
  assignment = models.ForeignKey(Assignment)
  student = models.ForeignKey(Student, related_name='instance')
  teammates = models.ManyToManyField(Student, blank=True, null=True, help_text='On Windows use Ctrl+Click to make multiple selection.  On a Mac use Cmd+Click to make multiple selection')
  status = models.CharField(max_length=255, choices=ASSIGNMENT_STATUS)
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
  note = RichTextField(null=True, blank=True)

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
  response = RichTextField(null=True, blank=True)
  responseFile = models.FileField(upload_to=upload_file_to, blank=True)
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = ('step_response', 'curriculum_question')


class QuestionResponseFile(models.Model):
  question_response = models.ForeignKey(QuestionResponse, related_name='response_file', null=False)
  file = models.FileField(upload_to=upload_file_to, null=False, blank=False)

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

class TrainingRequest(models.Model):
  name = models.CharField(max_length=255, blank=False, help_text="Name")
  email = models.EmailField(max_length=255, blank=False, help_text="Email")
  school = models.CharField(max_length=255, blank=False, help_text="School Name")
  subject = models.CharField(max_length=255, blank=False, help_text="Subject")
  created_date = models.DateTimeField(auto_now_add=True)


#signal used for is_active=False to is_active=True
@receiver(pre_save, sender=User, dispatch_uid='active')
def active(sender, instance, **kwargs):
  if instance.is_active and User.objects.filter(pk=instance.pk, is_active=False).exists():
    current_site = Site.objects.get_current()
    domain = current_site.domain

    send_mail('CT-STEM Account Activated',
              'Your account has been activated on Computational Thinking in STEM website http://%s.\r\n\r\n\
               You can login using the credentials created during registration.\r\n\r\n\
              -- CT-STEM Admin' % domain,
              settings.DEFAULT_FROM_EMAIL,
              [instance.email])
