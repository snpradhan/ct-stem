# -*- coding: utf-8 -*-


from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0016_auto_20151028_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='local_copy',
            field=models.FileField(upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
    ]
