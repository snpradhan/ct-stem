# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0131_curriculum_locked_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='research_category',
        ),
        migrations.AddField(
            model_name='question',
            name='research_category',
            field=models.ManyToManyField(related_name='questions', null=True, to='ctstem_app.ResearchCategory', blank=True),
        ),
    ]
