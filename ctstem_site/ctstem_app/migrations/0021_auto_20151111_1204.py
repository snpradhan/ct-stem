# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0020_auto_20151111_1203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='slug',
            field=models.SlugField(unique=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='slug',
            field=models.SlugField(unique=True, max_length=255),
        ),
    ]
