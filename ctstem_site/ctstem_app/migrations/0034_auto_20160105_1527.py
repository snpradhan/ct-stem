# -*- coding: utf-8 -*-


from django.db import models, migrations
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0033_auto_20160104_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessmentstep',
            name='teacher_notes',
            field=ckeditor_uploader.fields.RichTextUploadingField(null=True, blank=True),
        ),
    ]
