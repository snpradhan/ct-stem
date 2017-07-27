# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0112_auto_20170725_1327'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculumquestion',
            name='referenced_by',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
