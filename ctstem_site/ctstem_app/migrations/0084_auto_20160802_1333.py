# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0083_auto_20160722_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='answer_field_type',
            field=models.CharField(default=b'TF', max_length=2, choices=[('TA', 'Text Area'), ('TF', 'Text Field'), ('DD', 'Drop Down'), ('MS', 'Multi-Select'), ('MC', 'Multiple Choice'), ('MI', 'Multiple Choice w/ Images'), ('FI', 'File')]),
        ),
        migrations.AlterField(
            model_name='question',
            name='options',
            field=models.TextField(help_text=b'For dropdown, multi-select and multiple choice questions provide one option per line.\n For multiple choice w/ images provide one image url per line', null=True, blank=True),
        ),
    ]
