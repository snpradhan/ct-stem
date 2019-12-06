# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0079_auto_20160718_1334'),
    ]

    operations = [
        migrations.RenameField(
            model_name='curriculum',
            old_name='compatible_with',
            new_name='compatible_system',
        ),
    ]
