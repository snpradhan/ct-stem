# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0006_auto_20151009_1351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessmentstep',
            name='questions',
            field=models.ManyToManyField(to='ctstem_app.Question', through='ctstem_app.AssessmentQuestion', blank=True),
        ),
    ]
