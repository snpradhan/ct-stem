# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0054_category_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionresponse',
            name='responseFile',
            field=models.FileField(upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_field_type',
            field=models.CharField(max_length=2, choices=[('TA', 'Text Area'), ('TF', 'Text Field'), ('SB', 'Slider Bar'), ('DD', 'Drop Down'), ('MS', 'Multi-Select'), ('MC', 'Multiple Choice'), ('MC', 'Multiple Choice'), ('FI', 'File')]),
        ),
        migrations.AlterField(
            model_name='questionresponse',
            name='response',
            field=models.TextField(null=True, blank=True),
        ),
    ]
