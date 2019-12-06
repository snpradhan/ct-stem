# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0037_standard_short_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='ct_stem_practices',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='ngss_standards',
        ),
        migrations.DeleteModel(
            name='CTStemPractice',
        ),
        migrations.DeleteModel(
            name='NGSSStandard',
        ),
    ]
