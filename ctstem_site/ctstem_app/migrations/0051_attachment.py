# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0050_auto_20160126_1525'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=256)),
                ('file_object', models.FileField(upload_to=ctstem_app.models.upload_file_to)),
                ('lesson', models.ForeignKey(to='ctstem_app.Lesson')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
    ]
