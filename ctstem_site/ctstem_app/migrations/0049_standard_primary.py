# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0048_auto_20160125_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='standard',
            name='primary',
            field=models.BooleanField(default=False),
        ),
    ]
