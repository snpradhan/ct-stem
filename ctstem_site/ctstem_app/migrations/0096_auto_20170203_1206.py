# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0095_auto_20170202_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='assigned_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 3, 12, 6, 22, 412040)),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='level',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text=b'Student level', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='overview',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text=b'Curriculum overview', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='purpose',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text=b'Purpose of this curriculum', null=True, blank=True),
        ),
    ]
