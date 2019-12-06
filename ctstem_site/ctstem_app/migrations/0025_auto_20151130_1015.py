# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0024_auto_20151125_1037'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='lesson',
            unique_together=set([]),
        ),
    ]
