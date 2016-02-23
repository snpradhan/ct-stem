# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0055_auto_20160223_1025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='answer_field_type',
            field=models.CharField(max_length=2, choices=[('TA', 'Text Area'), ('TF', 'Text Field'), ('SB', 'Slider Bar'), ('DD', 'Drop Down'), ('MS', 'Multi-Select'), ('MC', 'Multiple Choice'), ('FI', 'File')]),
        ),
    ]
