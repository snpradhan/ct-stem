# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0039_auto_20160112_1126'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='abbrevation',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='school',
            name='school_code',
            field=models.CharField(unique=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='subject',
            name='name',
            field=models.CharField(max_length=256),
        ),
    ]
