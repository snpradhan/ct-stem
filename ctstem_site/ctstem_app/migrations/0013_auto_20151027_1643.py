# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0012_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessmentstep',
            name='teacher_notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='teacher_notes',
            field=models.TextField(null=True, blank=True),
        ),
    ]
