# -*- coding: utf-8 -*-


from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0063_auto_20160421_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='icon',
            field=models.ImageField(upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_field_type',
            field=models.CharField(max_length=2, choices=[('TA', 'Text Area'), ('TF', 'Text Field'), ('DD', 'Drop Down'), ('MS', 'Multi-Select'), ('MC', 'Multiple Choice'), ('FI', 'File')]),
        ),
    ]
