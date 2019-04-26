# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0151_auto_20181211_1201'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usergroup',
            options={'ordering': ['title']},
        ),
        migrations.AddField(
            model_name='usergroup',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 22, 19, 16, 10, 967657, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usergroup',
            name='modified_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 22, 19, 16, 21, 783183, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='authors',
            field=models.ManyToManyField(help_text=b'Select authors for this curriculum.', related_name='curriculum_authors', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='status',
            field=models.CharField(default=b'D', max_length=1, choices=[('D', 'Private'), ('P', 'Public'), ('A', 'Archived')]),
        ),
    ]
