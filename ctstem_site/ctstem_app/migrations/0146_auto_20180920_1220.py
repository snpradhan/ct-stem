# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0145_auto_20180727_1317'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='due_date',
        ),
        migrations.AddField(
            model_name='assignment',
            name='release',
            field=models.BooleanField(default=True),
        ),
    ]
