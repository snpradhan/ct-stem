# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0122_auto_20171011_1257'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
