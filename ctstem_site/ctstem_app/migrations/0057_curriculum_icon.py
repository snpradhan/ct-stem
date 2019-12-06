# -*- coding: utf-8 -*-


from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0056_auto_20160223_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='icon',
            field=models.FileField(upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
    ]
