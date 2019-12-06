# -*- coding: utf-8 -*-


from django.db import models, migrations
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0177_auto_20191021_1044'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='authors',
        ),
        migrations.RemoveField(
            model_name='publication',
            name='award',
        ),
        migrations.RemoveField(
            model_name='publication',
            name='journal',
        ),
        migrations.RemoveField(
            model_name='publication',
            name='local_copy',
        ),
        migrations.RemoveField(
            model_name='publication',
            name='pages',
        ),
        migrations.RemoveField(
            model_name='publication',
            name='publication_type',
        ),
        migrations.RemoveField(
            model_name='publication',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='publication',
            name='title',
        ),
        migrations.RemoveField(
            model_name='publication',
            name='year',
        ),
        migrations.AddField(
            model_name='publication',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(default=b'Enter publication', help_text=b'Enter publication details'),
        ),
    ]
