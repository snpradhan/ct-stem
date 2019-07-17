# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0167_curriculum_feature_rank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subcategory',
            name='title',
            field=models.CharField(max_length=512),
        ),
    ]
