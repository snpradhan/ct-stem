# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0108_auto_20170418_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='curriculum_type',
            field=models.CharField(max_length=1, choices=[('U', 'Unit'), ('L', 'Lesson Plan'), ('A', 'Assessment'), ('S', 'Survey')]),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ctstem_app.Curriculum', help_text=b'Select a unit if this lesson is part of one', null=True),
        ),
    ]
