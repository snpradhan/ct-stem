# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0046_teamrole_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='order',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='team',
            name='role',
            field=models.ForeignKey(related_name='members', to='ctstem_app.TeamRole'),
        ),
        migrations.AlterField(
            model_name='teamrole',
            name='order',
            field=models.IntegerField(unique=True),
        ),
    ]
