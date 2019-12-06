# -*- coding: utf-8 -*-


from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0073_auto_20160609_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='icon',
            field=models.ImageField(help_text=b'Upload 400x289 png image that represents this curriculum', upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='level',
            field=models.TextField(help_text=b'Student level'),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='purpose',
            field=models.TextField(help_text=b'Purpose of this curriculum'),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='subject',
            field=models.ManyToManyField(help_text=b'Select one or more subjects', to='ctstem_app.Subject', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='time',
            field=models.CharField(help_text=b'Estimated time students would spend on this curriculum', max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='title',
            field=models.CharField(help_text=b'Curriculum title', max_length=256),
        ),
        migrations.AlterField(
            model_name='step',
            name='title',
            field=models.CharField(help_text=b'Step title', max_length=256),
        ),
    ]
