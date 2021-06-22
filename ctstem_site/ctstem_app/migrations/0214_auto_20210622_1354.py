# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-22 18:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0213_assignment_realtime_feedback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='research_category',
            field=models.ManyToManyField(help_text='On Windows use Ctrl+Click to make multiple selection.  On a Mac use Cmd+Click to make multiple selection', related_name='questions', to='ctstem_app.ResearchCategory'),
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='shared_with',
            field=models.ManyToManyField(blank=True, help_text='Select teachers to share this class with.', related_name='shared_groups', to='ctstem_app.Teacher'),
        ),
    ]
