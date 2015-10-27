# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0003_auto_20151006_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='level',
            field=models.TextField(default='abc'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lesson',
            name='questions',
            field=models.ManyToManyField(to='ctstem_app.Question', through='ctstem_app.LessonQuestion', blank=True),
        ),
    ]
