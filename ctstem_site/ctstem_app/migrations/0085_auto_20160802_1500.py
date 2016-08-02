# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0084_auto_20160802_1333'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='teacher_only',
            field=models.BooleanField(default=False, choices=[(True, b'Yes'), (False, b'No')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='attachment',
            name='file_object',
            field=models.FileField(upload_to=ctstem_app.models.upload_file_to),
        ),
    ]
