# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ctstem_app.models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0093_auto_20170109_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='sketch_background',
            field=models.ImageField(null=True, upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='assigned_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 1, 11, 12, 59, 2, 636719)),
        ),
    ]
