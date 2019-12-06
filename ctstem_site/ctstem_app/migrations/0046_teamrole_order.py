# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0045_auto_20160115_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamrole',
            name='order',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
