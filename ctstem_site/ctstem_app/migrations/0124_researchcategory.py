# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0123_usergroup_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResearchCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(max_length=256, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
    ]
