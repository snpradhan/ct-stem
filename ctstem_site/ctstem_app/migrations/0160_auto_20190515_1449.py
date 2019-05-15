# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0159_auto_20190515_1247'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='questionfeedback',
            unique_together=set([('step_feedback', 'response')]),
        ),
        migrations.AlterUniqueTogether(
            name='stepfeedback',
            unique_together=set([('assignment_feedback', 'step_response')]),
        ),
    ]
