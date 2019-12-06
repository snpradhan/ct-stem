# -*- coding: utf-8 -*-


from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0140_auto_20180712_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='group_code',
            field=models.CharField(null=True, max_length=10),
        ),
    ]
