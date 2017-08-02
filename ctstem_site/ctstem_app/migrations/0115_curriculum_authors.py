# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ctstem_app', '0114_curriculum_acknowledgement'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='authors',
            field=models.ManyToManyField(related_name='curriculum_authors', to=settings.AUTH_USER_MODEL),
        ),
    ]
