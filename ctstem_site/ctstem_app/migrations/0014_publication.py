# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0013_auto_20151027_1643'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('authors', models.CharField(max_length=255)),
                ('year', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('journal', models.CharField(max_length=255)),
                ('pages', models.CharField(max_length=255, blank=True)),
                ('award', models.CharField(max_length=255, blank=True)),
                ('slug', models.SlugField(unique=True, max_length=255)),
                ('viewable', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('localCopy', models.FileField(upload_to=b'files/pubs/', blank=True)),
                ('weblink', models.URLField(blank=True)),
                ('pubType', models.CharField(max_length=255, choices=[('journal', 'Journal Articles'), ('book', 'Book Chapters'), ('refConfs', 'Refereed Conference Papers'), ('presentations', 'Presentations and Posters'), ('workshops', 'Workshop Papers'), ('others', 'Other Papers')])),
                ('pubAffil', models.CharField(max_length=255, choices=[('lab', 'TIDAL Lab'), ('personal', 'Personal')])),
            ],
        ),
    ]
