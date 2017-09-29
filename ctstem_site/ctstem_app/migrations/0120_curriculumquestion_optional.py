# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0119_assignmentnotes'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculumquestion',
            name='optional',
            field=models.BooleanField(default=False),
        ),
    ]
