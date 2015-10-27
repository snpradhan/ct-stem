# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0004_auto_20151007_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='content',
            field=tinymce.models.HTMLField(),
        ),
    ]
