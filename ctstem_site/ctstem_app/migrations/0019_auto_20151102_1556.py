# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0018_auto_20151029_1501'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='viewable',
        ),
        migrations.AlterField(
            model_name='assessmentstep',
            name='title',
            field=models.CharField(default='abc', max_length=256),
            preserve_default=False,
        ),
    ]
