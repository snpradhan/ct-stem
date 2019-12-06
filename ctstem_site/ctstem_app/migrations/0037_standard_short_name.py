# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0036_auto_20160107_1403'),
    ]

    operations = [
        migrations.AddField(
            model_name='standard',
            name='short_name',
            field=models.CharField(default='a', max_length=256),
            preserve_default=False,
        ),
    ]
