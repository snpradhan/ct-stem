# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0148_auto_20180921_1238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='options',
            field=models.TextField(help_text=b'Click on the &#9432; icon to see the Options Guide', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='sketch_background',
            field=models.ImageField(help_text=b'Upload 900x500 png background image for the sketch pad', null=True, upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
    ]
