# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0096_auto_20170203_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='assigned_date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
