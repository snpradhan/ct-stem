# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0074_auto_20160609_1349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='curriculum_type',
            field=models.CharField(max_length=1, choices=[('L', 'Lesson Plan'), ('A', 'Assessment'), ('S', 'Survey')]),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='level',
            field=models.TextField(help_text=b'Student level', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='overview',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='purpose',
            field=models.TextField(help_text=b'Purpose of this curriculum', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='taxonomy',
            field=models.ManyToManyField(to='ctstem_app.Subcategory', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='time',
            field=models.CharField(help_text=b'Estimated time students would spend on this curriculum', max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='title',
            field=models.CharField(help_text=b'Curriculum title', max_length=256, null=True, blank=True),
        ),
    ]
