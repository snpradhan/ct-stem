# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0023_auto_20151116_1246'),
    ]

    operations = [
        migrations.RenameField(
            model_name='researcher',
            old_name='permission_code',
            new_name='user_code',
        ),
        migrations.RenameField(
            model_name='teacher',
            old_name='permission_code',
            new_name='user_code',
        ),
    ]
