# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0149_auto_20181205_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='coteachers',
            field=models.ManyToManyField(to='ctstem_app.Teacher', null=True, blank=True),
        ),
    ]
