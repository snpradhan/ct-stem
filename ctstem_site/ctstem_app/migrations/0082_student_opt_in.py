# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0081_system_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='opt_in',
            field=models.CharField(default=b'U', max_length=1, choices=[('A', 'Agree'), ('D', 'Disagree')]),
        ),
    ]
