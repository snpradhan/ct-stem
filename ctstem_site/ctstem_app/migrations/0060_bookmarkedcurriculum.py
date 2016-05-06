# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0059_auto_20160401_1512'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookmarkedCurriculum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('curriculum', models.ForeignKey(to='ctstem_app.Curriculum')),
                ('teacher', models.ForeignKey(to='ctstem_app.Teacher')),
            ],
        ),
    ]