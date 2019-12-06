# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0065_remove_curriculum_modified_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='section',
            name='students',
        ),
        migrations.RemoveField(
            model_name='section',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='section',
            name='teacher',
        ),
        migrations.RemoveField(
            model_name='researcher',
            name='teachers',
        ),
        migrations.RemoveField(
            model_name='researcher',
            name='user_code',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='students',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='user_code',
        ),
        migrations.DeleteModel(
            name='Section',
        ),
    ]
