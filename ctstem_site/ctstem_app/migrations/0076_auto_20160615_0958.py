# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0075_auto_20160614_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='overview',
            field=models.TextField(default='abc'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='title',
            field=models.CharField(default='abc', help_text=b'Curriculum title', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='step',
            name='title',
            field=models.CharField(help_text=b'Step title', max_length=256, null=True, blank=True),
        ),
    ]
