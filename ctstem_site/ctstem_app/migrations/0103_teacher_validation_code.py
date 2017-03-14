# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0102_auto_20170303_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='validation_code',
            field=models.CharField(default='ABCDE', max_length=5),
            preserve_default=False,
        ),
    ]
