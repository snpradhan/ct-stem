# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0163_auto_20190612_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='acknowledgement',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text=b'Resources, models, and other material used in this curriculum; past authors/contributors', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='authors',
            field=models.ManyToManyField(help_text=b'Select authors for this curriculum', related_name='curriculum_authors', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='credits',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text=b'Author contributions', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='level',
            field=models.TextField(help_text=b'(ex. high school AP or Advanced Physics course)', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='overview',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text=b'Description of the unit; This text is shown to teachers and researchers only', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='shared_with',
            field=models.ManyToManyField(help_text=b'Select teachers to share this curriculum with before it is published', to='ctstem_app.Teacher', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='student_overview',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text=b'Description of what students will learn in this curriculum; This text is shown to students only', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='time',
            field=models.CharField(help_text=b'Estimated time students would spend on this curriculum (ex. 7-9 class periods of 45-50 minutes)', max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='title',
            field=models.CharField(help_text=b'Name of Unit or Lesson', max_length=256),
        ),
        migrations.AlterField(
            model_name='step',
            name='title',
            field=models.CharField(help_text=b'Page title', max_length=256, null=True, blank=True),
        ),
    ]
