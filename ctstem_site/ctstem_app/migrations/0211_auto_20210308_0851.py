# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-03-08 14:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0210_auto_20210305_0731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='topic_type',
            field=models.CharField(choices=[('teacher_guide', 'Teacher Guide'), ('faq', 'Help and FAQ')], max_length=255),
        ),
    ]
