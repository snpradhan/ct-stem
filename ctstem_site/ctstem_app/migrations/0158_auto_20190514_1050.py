# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0157_auto_20190425_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroup',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
    ]
