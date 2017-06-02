# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0108_auto_20170418_1105'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='shared_with',
            field=models.ManyToManyField(to='ctstem_app.Teacher', null=True, blank=True),
        ),
    ]
