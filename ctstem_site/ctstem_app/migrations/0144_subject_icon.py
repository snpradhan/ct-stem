# -*- coding: utf-8 -*-


from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0143_auto_20180712_1632'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='icon',
            field=models.ImageField(help_text=b'Upload 400x289 png image that represents this subject', upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
    ]
