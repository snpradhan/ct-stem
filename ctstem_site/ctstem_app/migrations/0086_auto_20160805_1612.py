# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0085_auto_20160802_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='overview',
            field=models.TextField(help_text=b'Curriculum overview', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_field_type',
            field=models.CharField(default=b'TF', max_length=2, choices=[('TA', 'Text Area'), ('TF', 'Text Field'), ('DD', 'Drop Down'), ('MS', 'Multi-Select'), ('MC', 'Multiple Choice'), ('MI', 'Multiple Choice w/ Images'), ('MH', 'Multiple Choice w/ Horizontal Layout'), ('FI', 'File')]),
        ),
    ]
