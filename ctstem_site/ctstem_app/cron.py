from ctstem_app import models
from datetime import datetime, timedelta
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.core import management
from django.utils import timezone
import subprocess

def cleanup_teacher_accounts():
  #get a list of teacher account created prior to 24 hrs and still inactive
  regEnd = datetime.today() - timedelta(hours = 24)
  print 'finding teachers registered before ', regEnd
  teachers = models.Teacher.objects.all().filter(user__is_active = False, user__date_joined__lt=regEnd)
  count = len(teachers)
  for teacher in teachers:
    #print 'deleting', teacher
    #check if this teacher created a new school, if so delete the school as well
    school = models.School.objects.get(id=teacher.school.id)
    if not school.is_active:
      school.delete()
    #send_deletion_email(teacher.user)
    teacher.user.delete()
  print '%d teacher accounts purged' % count

def send_deletion_email(user):
  send_mail('CT-STEM Account Deletion',
    ' \r\n \
    Your account on the CT-STEM website was not activated with in 24 hours of creation. \r\n\r\n \
    Therefore, your account is being deleted.  If you need to use our website, please register again.\r\n\r\n \
    -- CT-STEM Admin',
    settings.DEFAULT_FROM_EMAIL,
    [user.email])


def backup_db():
  print 'start db backup', datetime.today()
  #remove old backups from the file system
  cmd = 'rm %s/*'% settings.DBBACKUP_STORAGE_OPTIONS['location']
  subprocess.call(cmd, shell=True)
  management.call_command('dbbackup')
  cmd = 's3cmd --access_key=%s --secret_key=%s -s put %s/default-* s3://%s' % (settings.AWS_ACCESS_KEY_ID,
                                                                               settings.AWS_SECRET_ACCESS_KEY,
                                                                               settings.DBBACKUP_STORAGE_OPTIONS['location'],
                                                                               settings.DBBACKUP_AWS_S3_BUCKET)
  subprocess.call(cmd, shell=True)
  print 'end db backup', datetime.today()

