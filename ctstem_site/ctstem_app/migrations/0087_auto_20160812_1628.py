# -*- coding: utf-8 -*-


from django.db import models, migrations
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0086_auto_20160805_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='step',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(null=True, blank=True),
        ),
    ]
