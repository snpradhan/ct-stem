# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0038_auto_20160107_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='school_code',
            field=models.CharField(default='C8ED0', unique=True, max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='title',
            field=models.CharField(help_text=b'Group Title. Eg. Physics Section A', max_length=255),
        ),
    ]
