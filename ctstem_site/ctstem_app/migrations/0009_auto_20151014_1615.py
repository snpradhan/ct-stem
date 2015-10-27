# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0008_auto_20151014_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='content',
            field=tinymce.models.HTMLField(),
        ),
    ]
