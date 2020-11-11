# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-03 20:26
from __future__ import unicode_literals

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0206_auto_20201109_1420'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='releasechange',
            options={'ordering': ['change_type']},
        ),
        migrations.AlterModelOptions(
            name='releasenote',
            options={'ordering': ['-version']},
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='overview',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, help_text='Description of the curriculum', null=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='student_overview',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, help_text='Description of what students will learn in this curriculum', null=True),
        ),
        migrations.AlterField(
            model_name='releasechange',
            name='change_type',
            field=models.CharField(choices=[('A', 'Major Changes'), ('I', 'Minor Changes'), ('X', 'Bug Fixes')], max_length=1),
        ),
    ]
