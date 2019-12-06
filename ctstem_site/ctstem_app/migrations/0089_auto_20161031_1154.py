# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0088_teacher_consent'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='parental_consent',
            field=models.CharField(default=b'U', max_length=1, choices=[('A', 'I Agree'), ('D', 'I Disagree')]),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='assigned_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 10, 31, 11, 54, 4, 375819)),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_field_type',
            field=models.CharField(default=b'TF', max_length=2, choices=[('TA', 'Text Area'), ('TF', 'Text Field'), ('DD', 'Drop Down'), ('MS', 'Multi-Select'), ('MC', 'Multiple Choice'), ('MI', 'Multiple Choice w/ Images'), ('MH', 'Multiple Choice w/ Horizontal Layout'), ('FI', 'File'), ('SK', 'Sketch')]),
        ),
    ]
