from ctstem_app import models

def group_assignment_dropdown_list(groups, for_student_inbox=True, disable_unit=True):
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

  assignment_list = {k: v for k, v in sorted(assignment_list.items(), key=lambda item: item[1]['title'].lower())}
  if for_student_inbox:
    assignment_choices = [('', '---------')]
  else:
    assignment_choices = [('', 'Select an Assignment')]
  for curriculum_id, details in assignment_list.items():
    if 'lessons' in details.keys():
      if for_student_inbox or not disable_unit:
        assignment_choices.append((curriculum_id, details['title']))
      else:
        assignment_choices.append(('', {'label': details['title'], 'disabled': True}))
      for order in sorted(details['lessons']):
        assignment_choices.append((details['lessons'][order].id, '-----  '+details['lessons'][order].title))
    else:
      assignment_choices.append((curriculum_id, details['title']))

  return assignment_choices

def group_dropdown_list(groups):
  group_choices = [('', '---------')]
  for group in groups:
    group_choices.append((group.id, group.title))

  return group_choices

def is_list_empty(arr):
  if len(arr) == 0:
    return True
  else:
    if isinstance(arr, list):
      empty = True
      for item in arr:
        empty = empty and is_list_empty(item)
        if not empty:
          break
      return empty
    else:
      return False

def student_dropdown_list(students, anonymize=False):
  student_choices = [('', 'Select a Student')]
  for student in students:
    if anonymize:
      student_choices.append((student.id, 'xxxxxxxxxxx'))
    else:
      student_choices.append((student.id, student))
  return student_choices

def question_dropdown_list(questions):
  question_choices = [('', 'Select a Question')]
  for question in questions:
    question_choices.append((question.id, 'Q '+str(question.step.order)+'.'+str(question.order)))
  return question_choices

