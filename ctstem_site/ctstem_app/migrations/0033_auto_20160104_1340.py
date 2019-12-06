# -*- coding: utf-8 -*-


from django.db import models, migrations
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0032_auto_20160104_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessmentstep',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
        migrations.AlterField(
            model_name='lessonactivity',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_text',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]
