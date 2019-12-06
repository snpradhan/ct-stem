# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0092_auto_20170109_1246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='assigned_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 1, 9, 14, 44, 53, 670695)),
        ),
    ]
