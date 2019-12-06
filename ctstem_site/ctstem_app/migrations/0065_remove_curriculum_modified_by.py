# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0064_auto_20160504_1058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='curriculum',
            name='modified_by',
        ),
    ]
