# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0010_auto_20151014_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='ctstem_app.Assessment', null=True),
        ),
        migrations.AddField(
            model_name='assessment',
            name='version',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='assessmentstep',
            name='teacher_notes',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lesson',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='ctstem_app.Lesson', null=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='teacher_notes',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lesson',
            name='version',
            field=models.IntegerField(default=1),
        ),
    ]
