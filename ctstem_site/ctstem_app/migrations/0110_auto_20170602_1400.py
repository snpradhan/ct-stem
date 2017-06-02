# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0109_curriculum_shared_with'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='shared_with',
            field=models.ManyToManyField(help_text=b'Select teachers to share this curriculum with before it is published.', to='ctstem_app.Teacher', null=True, blank=True),
        ),
    ]
