# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0089_auto_20161031_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='assigned_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 10, 31, 12, 37, 34, 659589)),
        ),
        migrations.AlterField(
            model_name='student',
            name='parental_consent',
            field=models.CharField(default=b'U', max_length=1, choices=[('U', 'Unknown'), ('A', 'Agree'), ('D', 'Disagree')]),
        ),
    ]
