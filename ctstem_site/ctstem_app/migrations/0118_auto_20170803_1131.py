# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0117_curriculum_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='order',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
