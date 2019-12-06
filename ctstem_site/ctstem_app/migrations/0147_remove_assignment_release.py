# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0146_auto_20180920_1220'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='release',
        ),
    ]
