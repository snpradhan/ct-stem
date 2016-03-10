# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0057_curriculum_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentinstance',
            name='status',
            field=models.CharField(max_length=255, choices=[('N', 'New'), ('P', 'In Progress'), ('S', 'Submitted'), ('F', 'Feedback Ready'), ('A', 'Archived')]),
        ),
        migrations.AlterUniqueTogether(
            name='assignmentstepresponse',
            unique_together=set([('instance', 'step')]),
        ),
        migrations.AlterUniqueTogether(
            name='questionresponse',
            unique_together=set([('step_response', 'curriculum_question')]),
        ),
    ]
