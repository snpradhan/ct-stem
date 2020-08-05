from ctstem_app import models, views

def associate_user_role(strategy, details, backend, user=None, *args, **kwargs):
  group_code = strategy.session_get('group_code')
  if group_code:
    #student
    group = models.UserGroup.objects.get(group_code__iexact=group_code)
    if(kwargs.get('is_new')):
      student = models.Student.objects.create(user=user, school=group.teacher.school)
    else:
      student = models.Student.objects.get_or_create(user=user)
      student.school = group.teacher.school
      student.save()

    membership, created = models.Membership.objects.get_or_create(student=student, group=group)
    views.send_added_to_group_confirmation_email(user.email, group)
  else:
    if(kwargs.get('is_new')):
      #teacher
      validation_code = views.get_random_string(length=5)
      teacher = models.Teacher.objects.create(user=user, validation_code=validation_code)
