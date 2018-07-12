# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0142_auto_20180712_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroup',
            name='group_code',
            field=models.CharField(default=ctstem_app.models.generate_code_helper, unique=True, max_length=10),
        ),
    ]
