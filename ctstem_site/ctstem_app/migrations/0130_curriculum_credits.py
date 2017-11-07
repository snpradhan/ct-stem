# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0129_remove_curriculum_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='credits',
            field=ckeditor_uploader.fields.RichTextUploadingField(null=True, blank=True),
        ),
    ]
