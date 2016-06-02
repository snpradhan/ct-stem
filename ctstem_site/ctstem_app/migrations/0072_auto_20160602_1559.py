# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0071_remove_researcher_school'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='answer_field_type',
            field=models.CharField(default=b'TF', max_length=2, choices=[('TA', 'Text Area'), ('TF', 'Text Field'), ('DD', 'Drop Down'), ('MS', 'Multi-Select'), ('MC', 'Multiple Choice'), ('FI', 'File')]),
        ),
    ]
