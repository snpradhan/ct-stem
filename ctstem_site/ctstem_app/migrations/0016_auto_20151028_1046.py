# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0015_auto_20151028_1043'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publication',
            old_name='url',
            new_name='web_link',
        ),
    ]
