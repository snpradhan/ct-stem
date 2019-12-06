# -*- coding: utf-8 -*-


from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0155_auto_20190131_1257'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='curriculum',
            name='author',
        ),
        migrations.AlterField(
            model_name='category',
            name='icon',
            field=models.ImageField(help_text=b'Upload an image at least 400x289 in resolution that represents this category', null=True, upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='icon',
            field=models.ImageField(help_text=b'Upload an image at least 400x289 in resolution that represents this curriculum', upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='sketch_background',
            field=models.ImageField(help_text=b'Upload a background image at least 900x500 in resolution for the sketch pad', null=True, upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
        migrations.AlterField(
            model_name='questionresponsefile',
            name='file',
            field=models.FileField(help_text=b'Upload a file less than 5 MB in size.', upload_to=ctstem_app.models.upload_file_to),
        ),
        migrations.AlterField(
            model_name='subject',
            name='icon',
            field=models.ImageField(help_text=b'Upload an image at least 400x289 in resolution that represents this subject', upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='icon',
            field=models.ImageField(help_text=b'Upload an image at least 400x289 in resolution that represents this class', upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
    ]
