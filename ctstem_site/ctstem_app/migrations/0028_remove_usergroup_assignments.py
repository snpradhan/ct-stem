# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0027_auto_20151204_1019'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usergroup',
            name='assignments',
        ),
    ]
