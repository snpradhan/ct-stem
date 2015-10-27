# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0007_auto_20151009_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ctstempractice',
            name='category',
            field=models.CharField(max_length=2, choices=[('DA', 'Data Analysis'), ('MS', 'Modeling & Simulation'), ('CP', 'Computational Problem Solving'), ('ST', 'Systems Thinking')]),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='content',
            field=models.TextField(),
        ),
    ]
