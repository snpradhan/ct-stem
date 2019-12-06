# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0128_auto_20171024_1314'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='curriculum',
            name='slug',
        ),
    ]
