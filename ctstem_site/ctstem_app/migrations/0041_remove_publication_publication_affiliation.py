# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0040_auto_20160112_1308'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='publication_affiliation',
        ),
    ]
