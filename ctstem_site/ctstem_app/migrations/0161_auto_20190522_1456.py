# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0160_auto_20190515_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentinstance',
            name='status',
            field=models.CharField(default=b'N', max_length=255, choices=[('N', 'New'), ('P', 'In Progress'), ('S', 'Submitted'), ('F', 'Feedback Ready'), ('A', 'Archived')]),
        ),
    ]
