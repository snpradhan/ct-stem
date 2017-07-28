# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0113_curriculumquestion_referenced_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='acknowledgement',
            field=ckeditor_uploader.fields.RichTextUploadingField(null=True, blank=True),
        ),
    ]
