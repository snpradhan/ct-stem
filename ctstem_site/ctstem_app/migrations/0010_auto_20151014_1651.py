# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0009_auto_20151014_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='content',
            field=models.TextField(),
        ),
    ]
