# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0017_auto_20151028_1301'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lessonquestion',
            options={'ordering': ['order']},
        ),
        migrations.RemoveField(
            model_name='question',
            name='owner',
        ),
    ]
