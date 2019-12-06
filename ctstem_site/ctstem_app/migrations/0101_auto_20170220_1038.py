# -*- coding: utf-8 -*-


from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0100_questionresponsefile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionresponsefile',
            name='file',
            field=models.FileField(upload_to=ctstem_app.models.upload_file_to),
        ),
    ]
