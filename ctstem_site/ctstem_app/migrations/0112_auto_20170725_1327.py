# -*- coding: utf-8 -*-


from django.db import models, migrations
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0111_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='student_overview',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text=b'Curriculum overview for students', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='overview',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text=b'Curriculum overview for teachers', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='unit',
            field=models.ForeignKey(related_name='underlying_curriculum', blank=True, to='ctstem_app.Curriculum', help_text=b'Select a unit if this lesson is part of one', null=True),
        ),
    ]
