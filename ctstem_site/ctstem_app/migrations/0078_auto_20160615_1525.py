# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0077_auto_20160615_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentinstance',
            name='teammates',
            field=models.ManyToManyField(help_text=b'Use Cmd+Click to make multiple selection', to='ctstem_app.Student', null=True, blank=True),
        ),
    ]
