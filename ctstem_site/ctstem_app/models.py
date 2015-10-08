from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField

LESSON_STATUS_CHOICES = (
    (u'D', u'Draft'),
    (u'P', u'Published'),
)

FIELD_TYPE_CHOICES = (
    (u'TA', u'Text Area'),
    (u'TF', u'Text Field'),
    (u'SB', u'Slider Bar'),
    (u'DD', u'Drop Down'),
    (u'MS', u'Multi-Select'),
    (u'MC', u'Multiple Choice'),
)
CT_STEW_PRACTICE_CATEGORY = (
    (u'DA', u'Data Analysis'),
    (u'MS', u'Modeling & Simulation'),
    (u'CPS', u'Computational Problem Solving'),
    (u'ST', u'Systems Thinking'),
)

SUBJECT_CHOICES = (
    (u'PHYSICS', u'PHYSICS'),
    (u'BIOLOGY', u'BIOLOGY'),
    (u'CHEMISTRY', u'CHEMISTRY'),
    (u'MATH', u'MATH'),
    (u'ASTRONOMY', u'ASTRONOMY'),
    (u'EARTH SCIENCE', u'EARTH SCIENCE'),
    (u'BIOTECHNOLOGY', u'BIOTECHNOLOGY'),
    (u'GENETICS', u'GENETICS'),
    (u'PHYSIOLOGY', u'PHYSIOLOGY'),
    (u'HUMAN ANATOMY', u'HUMAN ANATOMY'),
    (u'ENVIRONMENTAL SCIENCE', u'ENVIRONMENTAL SCIENCE'),
    (u'SPACE SCIENCE', u'SPACE SCIENCE'),
    (u'FORENSIC SCIENCE', u'FORENSIC SCIENCE'),
    (u'PHYSICAL SCIENCE', u'PHYSICAL SCIENCE'),
    (u'NATURAL SCIENCE', u'NATURAL SCIENCE'),
    (u'GEOLOGY', u'GEOLOGY'),
    (u'ECOLOGY', u'ECOLOGY'),
    (u'GENERAL SCIENCE', u'GENERAL SCIENCE'),
)

USER_ROLE_CHOICES = (
    (u'T', u'Teacher'),
    (u'R', u'Researcher/School Admin'),
    (u'S', u'Student'),
    (u'A', u'Site Administrator'),

)

def upload_image_to(instance, filename):
  import os
  from django.utils.timezone import now
  filename_base, filename_ext = os.path.splitext(filename)
  print filename
  if isinstance(instance, Lesson):
      return 'lesson/%s%s' % (instance.title, filename_ext.lower(),)
  elif isinstance(instance, Assessment):
      return 'assessment/%s%s' % (instance.name, filename_ext.lower(),)
  return 'misc/%s%s' % (instance.id,filename_ext.lower(),)

# Create your models here.

# Lesson model
class Lesson (models.Model):
  title = models.CharField(null=False, max_length=256, unique=True)
  time = models.CharField(null=True, max_length=256)
  level = models.TextField(null=False)
  purpose = models.TextField(null=False)
  overview = models.TextField(null=False)
  content = HTMLField(null=False)
  status = models.CharField(max_length=1, default='D', choices=LESSON_STATUS_CHOICES)
  subject = models.ManyToManyField('Subject', null=False)
  #image = models.ImageField(upload_to=upload_image_to, null=True, blank=True)
  questions = models.ManyToManyField('Question', through='LessonQuestion', blank=True)
  ngss_standards = models.ManyToManyField('NGSSStandard')
  ct_stem_practices = models.ManyToManyField('CTStemPractice')
  author = models.ForeignKey(User, null=False, related_name='lesson_author')
  modified_by = models.ForeignKey(User, null=False, related_name='lesson_modifier')
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

  class Meta:
      ordering = ['-id']

  def __unicode__(self):
      return u'%s' % (self.title)

# Assessment model
class Assessment (models.Model):
  title = models.CharField(null=False, max_length=256, unique=True)
  time = models.CharField(null=True, max_length=256)
  overview = models.TextField(null=False)
  status = models.CharField(max_length=1, default='D', choices=LESSON_STATUS_CHOICES)
  subject = models.ManyToManyField('Subject', null=False)
  #image = models.ImageField(upload_to=upload_image_to, null=True, blank=True)
  ngss_standards = models.ManyToManyField('NGSSStandard')
  ct_stem_practices = models.ManyToManyField('CTStemPractice')
  author = models.ForeignKey(User, null=False, related_name='assessment_author')
  modified_by = models.ForeignKey(User, null=False, related_name='assessment_modifier')
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

  class Meta:
      ordering = ['-id']

  def __unicode__(self):
      return u'%s' % (self.title)

# Assessment Step model
# An assessment has one or more assessment steps
class AssessmentStep(models.Model):
  assessment_id = models.ForeignKey(Assessment, null=False)
  title = models.CharField(null=True, max_length=256)
  order = models.IntegerField(null=True)
  content = models.TextField(null=False)
  questions = models.ManyToManyField('Question', through='AssessmentQuestion')

# Question model
# A bank of questions that can be resued across assessments and lessons
class Question(models.Model):
  question_text = models.TextField(null=False, blank=False)
  owner = models.ForeignKey(User, null=False)
  answer_field_type = models.CharField(null=False, max_length=2, choices=FIELD_TYPE_CHOICES)
  options = models.TextField(null=True, blank=True)
  answer = models.TextField(null=True, blank=True)

  def __unicode__(self):
      return u'%s' % (self.question_text)

# A relation between Lesson and Question models
class LessonQuestion(models.Model):
  question = models.ForeignKey(Question)
  lesson = models.ForeignKey(Lesson)
  order = models.IntegerField(null=True)

  def __unicode__(self):
      return u'%s' % (self.question.question_text)

# A relation between Assessment Step and Question models
class AssessmentQuestion(models.Model):
  question = models.ForeignKey(Question)
  assessment_step = models.ForeignKey(AssessmentStep)
  order = models.IntegerField(null=True)

# Subject model
class Subject(models.Model):
  name = models.CharField(null=False, max_length=256, choices=SUBJECT_CHOICES)

  def __unicode__(self):
      return u'%s' % (self.name)

# NGSS Standard model
# This model will be populated from an external source
# This model has many to many relation with Lesson and Assessment models
class NGSSStandard(models.Model):
  title = models.CharField(null=False, max_length=256)
  description = models.TextField(null=True, blank=True)

  def __unicode__(self):
      return u'%s' % (self.title)

# CT Stem Practice model
# This model has many to many relation with Lesson and Assessment models
class CTStemPractice(models.Model):
  category = models.CharField(null=False, max_length=2, choices=CT_STEW_PRACTICE_CATEGORY)
  title = models.CharField(null=True, max_length=256)
  overview = models.TextField(null=False)
  order = models.IntegerField(null=True)

  def __unicode__(self):
      return u'%s-%s' % (self.category, self.title)

# School model
class School(models.Model):
  name = models.CharField(null=False, max_length=256)
  city = models.CharField(null=False, max_length=256)

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
  permission_code = models.CharField(null=False, max_length=256, unique=True)

  def __unicode__(self):
      return u'%s' % (self.user.get_full_name())

# Researcher model
# This model represents researchers, school admins and school principals
class Researcher(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, related_name="researcher")
  school = models.ForeignKey(School)
  teachers = models.ManyToManyField(Teacher, blank=True)
  permission_code = models.CharField(null=False, max_length=256, unique=True)

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
