# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ctstem_app', '0105_auto_20170411_0959'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='created_by',
            field=models.ForeignKey(related_name='school_creator', default='1', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='school',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 13, 15, 28, 29, 560879, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
