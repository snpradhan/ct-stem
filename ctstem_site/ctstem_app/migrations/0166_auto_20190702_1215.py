# -*- coding: utf-8 -*-


from django.db import models, migrations
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0165_team_current'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='overview',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text=b'Description of the curriculum; This text is shown to teachers and researchers only', null=True, blank=True),
        ),
    ]
