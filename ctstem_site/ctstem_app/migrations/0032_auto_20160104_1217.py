# -*- coding: utf-8 -*-


from django.db import models, migrations
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0031_auto_20151209_1052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessmentstep',
            name='assessment',
            field=models.ForeignKey(related_name='assessment_steps', to='ctstem_app.Assessment'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='teacher_notes',
            field=ckeditor_uploader.fields.RichTextUploadingField(null=True, blank=True),
        ),
    ]
