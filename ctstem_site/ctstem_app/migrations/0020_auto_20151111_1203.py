# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0019_auto_20151102_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='slug',
            field=models.SlugField(default='abc', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lesson',
            name='slug',
            field=models.SlugField(default='abc', max_length=255),
            preserve_default=False,
        ),
    ]
