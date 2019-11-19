# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0178_auto_20191119_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='description',
            field=ckeditor.fields.RichTextField(default=b'Enter publication', help_text=b'Enter publication details'),
        ),
    ]
