# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0179_auto_20191119_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='status',
            field=models.CharField(default=b'D', max_length=1, choices=[('D', 'Private'), ('P', 'Public'), ('A', 'Archived'), ('R', 'Deleted')]),
        ),
    ]
