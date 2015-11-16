# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0022_auto_20151112_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='status',
            field=models.CharField(default=b'D', max_length=1, choices=[('D', 'Draft'), ('P', 'Published'), ('A', 'Archived')]),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='title',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='status',
            field=models.CharField(default=b'D', max_length=1, choices=[('D', 'Draft'), ('P', 'Published'), ('A', 'Archived')]),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='title',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterUniqueTogether(
            name='assessment',
            unique_together=set([('title', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='lesson',
            unique_together=set([('title', 'version')]),
        ),
    ]
