# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0154_auto_20190129_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='authors',
            field=models.ManyToManyField(related_name='curriculum_authors', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='status',
            field=models.CharField(default=b'D', max_length=1, choices=[('D', 'Draft'), ('P', 'Published'), ('A', 'Archived')]),
        ),
    ]
