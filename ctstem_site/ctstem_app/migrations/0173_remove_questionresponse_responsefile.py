# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0172_auto_20190816_1101'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questionresponse',
            name='responseFile',
        ),
    ]
