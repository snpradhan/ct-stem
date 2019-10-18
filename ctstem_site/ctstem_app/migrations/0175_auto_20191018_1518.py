# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0174_auto_20190919_1056'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publication',
            old_name='created',
            new_name='created_date',
        ),
        migrations.AddField(
            model_name='publication',
            name='modified_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 10, 18, 20, 18, 5, 708028, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='publication',
            name='order',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
