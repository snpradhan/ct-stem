# -*- coding: utf-8 -*-


from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0152_auto_20190122_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='icon',
            field=models.ImageField(help_text=b'Upload 400x289 png image that represents this class', upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
    ]
