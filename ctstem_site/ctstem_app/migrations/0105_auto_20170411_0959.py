# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0104_school_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='school',
            name='status',
        ),
        migrations.AddField(
            model_name='school',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
