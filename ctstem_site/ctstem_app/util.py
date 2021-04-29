from ctstem_app import models

def group_assignment_dropdown_list(groups):
  curricula = models.Curriculum.objects.all().filter(assignments__group__in=groups).exclude(status='R').distinct().order_by('title')
  assignment_list = {}
  for curriculum in curricula:
    if curriculum.curriculum_type in ['L', 'A'] and curriculum.unit is not None:
      if curriculum.order:
        lesson_key = curriculum.order
      else:
        lesson_key = curriculum.id

      if curriculum.unit.id in assignment_list:
        assignment_list[curriculum.unit.id]['lessons'][lesson_key] = curriculum
      else:
        assignment_list[curriculum.unit.id] = {'title': curriculum.unit.title, 'lessons': {lesson_key: curriculum}}
    else:
      assignment_list[curriculum.id] = {'title': curriculum.title}

  assignment_list = {k: v for k, v in sorted(assignment_list.items(), key=lambda item: item[1]['title'])}
  assignment_choices = [('', '---------')]
  for curriculum_id, details in assignment_list.items():
    assignment_choices.append((curriculum_id, details['title']))
    if 'lessons' in details.keys():
      for order in sorted(details['lessons']):
        assignment_choices.append((details['lessons'][order].id, '-----  '+details['lessons'][order].title))

  return assignment_choices

def group_dropdown_list(groups):
  group_choices = [('', '---------')]
  for group in groups:
    group_choices.append((group.id, group.title))

  return group_choices
