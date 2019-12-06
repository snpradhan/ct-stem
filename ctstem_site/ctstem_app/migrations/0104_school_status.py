# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0103_teacher_validation_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='status',
            field=models.CharField(default=b'I', max_length=1, choices=[('A', 'Active'), ('I', 'Inactive')]),
        ),
    ]
