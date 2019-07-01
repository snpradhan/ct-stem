# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0164_auto_20190626_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='current',
            field=models.BooleanField(default=True),
        ),
    ]
