# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0080_auto_20160718_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='system',
            name='icon',
            field=models.CharField(default='abc', max_length=256),
            preserve_default=False,
        ),
    ]
