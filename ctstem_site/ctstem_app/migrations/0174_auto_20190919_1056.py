# -*- coding: utf-8 -*-


from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0173_remove_questionresponse_responsefile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='icon',
            field=models.ImageField(help_text=b'Upload an image at least 400x289 in resolution that represents this curriculum', null=True, upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='icon',
            field=models.ImageField(help_text=b'Upload an image at least 400x289 in resolution that represents this subject', null=True, upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='icon',
            field=models.ImageField(help_text=b'Upload an image at least 400x289 in resolution that represents this class', null=True, upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
    ]
