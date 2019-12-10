# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='researcher',
            name='permission_code',
            field=models.CharField(default='abcd', unique=True, max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='student',
            name='school',
            field=models.ForeignKey(default=1, to='ctstem_app.School', on_delete=models.SET_NULL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='teacher',
            name='permission_code',
            field=models.CharField(default='xyz', unique=True, max_length=256),
            preserve_default=False,
        ),
    ]
