# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0126_auto_20171024_1226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='researchcategory',
            name='category',
            field=models.CharField(default='abc', max_length=256),
            preserve_default=False,
        ),
    ]
