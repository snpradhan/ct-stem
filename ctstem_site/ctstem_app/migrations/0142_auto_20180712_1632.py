# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import string
from django.utils.crypto import get_random_string

def generate_code_for_group(apps, schema_editor):
    code_list = []
    SchoolModel = apps.get_model('ctstem_app', 'School')
    schools = SchoolModel.objects.all()
    for school in schools:
        code_list.append(school.school_code)

    GroupModel = apps.get_model('ctstem_app', 'UserGroup')
    groups = GroupModel.objects.all()

    allowed_chars = ''.join((string.uppercase, string.digits))
    for group in groups:
        code = get_random_string(length=5, allowed_chars=allowed_chars)
        while code in code_list:
            code = get_random_string(length=5, allowed_chars=allowed_chars)
        group.group_code = code
        group.save()
        code_list.append(code)



class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0141_usergroup_group_code'),
    ]

    operations = [
      migrations.RunPython(generate_code_for_group, reverse_code=migrations.RunPython.noop),
    ]
