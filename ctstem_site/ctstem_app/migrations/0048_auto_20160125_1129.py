# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0047_auto_20160125_1123'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='team',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='teamrole',
            options={'ordering': ['order']},
        ),
    ]
