# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0109_auto_20170426_1140'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='unit',
            field=models.ForeignKey(related_name='underlying_curriculum', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ctstem_app.Curriculum', help_text=b'Select a unit if this lesson is part of one', null=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='parent',
            field=models.ForeignKey(related_name='children', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ctstem_app.Curriculum', null=True),
        ),
    ]
