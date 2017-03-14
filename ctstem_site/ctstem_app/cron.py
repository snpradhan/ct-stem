from ctstem_app import models
from datetime import datetime, timedelta
from django.core.mail import send_mail, EmailMessage
from django.conf import settings

def cleanup_teacher_accounts():
  #get a list of teacher account created between 24-48 hr window and are still inactive
  regStart = datetime.today() - timedelta(hours = 48)
  regEnd = datetime.today() - timedelta(hours = 24)
  print 'finding teachers registered between ', regStart, 'and', regEnd
  teachers = models.Teacher.objects.all().filter(user__is_active = False, user__date_joined__range=(regStart, regEnd))
  for teacher in teachers:
    print 'deleting', teacher
    send_deletion_email(teacher.user)
    teacher.user.delete()
  print 'done teacher cleanup'

def send_deletion_email(user):
  send_mail('CT-STEM Account Deletion',
    ' \r\n \
    Your account on the CT-STEM website was not activated with in 24 hours of creation. \r\n\r\n \
    Therefore, your account is being deleted.  If you need to use our website, please register again.\r\n\r\n \
    -- CT-STEM Admin',
    settings.DEFAULT_FROM_EMAIL,
    [user.email])
