# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0106_auto_20170413_1028'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='school',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='school',
            name='created_date',
        ),
    ]
