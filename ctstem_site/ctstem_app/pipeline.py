from ctstem_app import models, views
from ctstem_app.exceptions import GoogleLoginException
from django.contrib import messages
from django import shortcuts
from django.contrib.auth.models import User

def create_student(strategy, details, backend, user=None, *args, **kwargs):
  group_code = strategy.session_get('group_code')
  if group_code:
    #student
    group = models.UserGroup.objects.get(group_code__iexact=group_code)
    student = None
    #new student logging in for the first time
    if kwargs.get('is_new'):
      if user is None:
        username = kwargs.get('username')
        response = kwargs.get('response')
        email = response.get('email')
        first_name = response.get('given_name')
        last_name = response.get('family_name')
        password = User.objects.make_random_password()
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

      student = models.Student.objects.create(user=user, school=group.teacher.school)
    else:
      #existing user logging in with group code
      if user:
        try:
          student = models.Student.objects.get(user=user)
          student.school = group.teacher.school
          student.save()
        except models.Student.DoesNotExist:
          raise GoogleLoginException('Sorry, you are using an invalid link to login.  Please use the Login button above to login.')

    if student:
      membership, created = models.Membership.objects.get_or_create(student=student, group=group)
      views.send_added_to_group_confirmation_email(user.email, group)

    return {'user': user,
            'is_new': kwargs.get('is_new')}
  else:

    if kwargs.get('is_new'):
      #teacher
      #validation_code = views.get_random_string(length=5)
      #teacher = models.Teacher.objects.create(user=user, validation_code=validation_code)
      raise GoogleLoginException('Sorry, you do not yet have an account.  \
        If you are a Teacher, please register for an account using the Register button.  \
        If you are a Student, please use the link provided by your teacher to register.')
    elif not user.is_active:
      raise GoogleLoginException('Sorry, your account is inactive and you cannot \
         Login at this time. If you are a teacher, validate your account using the link \
         sent to your email.  If you are a student, ask your teacher to activate your account.')
