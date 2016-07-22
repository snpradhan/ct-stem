# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0082_student_opt_in'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='opt_in',
        ),
        migrations.AddField(
            model_name='student',
            name='consent',
            field=models.CharField(default=b'U', max_length=1, choices=[('A', 'I Agree'), ('D', 'I Disagree')]),
        ),
    ]
