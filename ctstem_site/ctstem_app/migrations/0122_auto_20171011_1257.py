# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0121_auto_20171011_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentnotes',
            name='note',
            field=ckeditor.fields.RichTextField(null=True, blank=True),
        ),
    ]
