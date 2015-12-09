# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0030_auto_20151207_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignmentinstance',
            name='modified_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 9, 16, 52, 47, 650175, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='assessmentquestion',
            name='question',
            field=models.ForeignKey(related_name='assessment_question', to='ctstem_app.Question'),
        ),
    ]
