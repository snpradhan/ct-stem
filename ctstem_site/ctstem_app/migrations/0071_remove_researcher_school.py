# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0070_schooladministrator'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='researcher',
            name='school',
        ),
    ]
