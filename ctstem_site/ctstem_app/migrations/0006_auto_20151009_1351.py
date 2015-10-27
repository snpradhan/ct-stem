# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0005_auto_20151007_1449'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assessmentstep',
            old_name='assessment_id',
            new_name='assessment',
        ),
    ]
