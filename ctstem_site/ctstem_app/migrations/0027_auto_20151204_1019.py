# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0026_auto_20151203_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 4, 16, 19, 39, 184453, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
