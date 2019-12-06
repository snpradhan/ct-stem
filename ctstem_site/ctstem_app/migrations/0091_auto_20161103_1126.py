# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0090_auto_20161031_1237'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignmentinstance',
            name='time_spent',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='assigned_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 3, 11, 26, 53, 731921)),
        ),
    ]
