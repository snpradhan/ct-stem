# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0156_auto_20190401_1311'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='display_other_option',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='order',
            field=models.IntegerField(help_text=b'Order within the Unit', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='unit',
            field=models.ForeignKey(related_name='underlying_curriculum', blank=True, to='ctstem_app.Curriculum', help_text=b'Select a unit if this curriculum is part of one', null=True),
        ),
    ]
