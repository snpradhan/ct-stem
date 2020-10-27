# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-08-11 18:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0197_auto_20200811_0832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='researchcategory',
            name='flag',
            field=models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=False, help_text='Questions with category that are flagged will be identified as such.'),
        ),
    ]