# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0116_auto_20170802_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='order',
            field=models.IntegerField(null=True),
        ),
    ]
