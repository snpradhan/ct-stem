# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0176_auto_20191018_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='curriculum_type',
            field=models.CharField(max_length=1, choices=[('U', 'Unit'), ('L', 'Lesson Plan'), ('A', 'Assessment')]),
        ),
    ]
