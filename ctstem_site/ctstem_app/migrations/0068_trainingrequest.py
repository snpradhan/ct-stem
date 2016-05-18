# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0067_category_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrainingRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Name', max_length=255)),
                ('email', models.CharField(help_text=b'Email', max_length=255)),
                ('school', models.CharField(help_text=b'School Name', max_length=255)),
                ('requester_role', models.CharField(help_text=b'I am:', max_length=255, choices=[('', 'I am:'), ('T', 'Teacher'), ('R', 'Researcher'), ('A', 'Administrator'), ('O', 'Other')])),
                ('notes', models.TextField(help_text=b'Notes')),
            ],
        ),
    ]
