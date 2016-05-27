# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ctstem_app', '0069_auto_20160518_1706'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolAdministrator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('school', models.ForeignKey(to='ctstem_app.School')),
                ('user', models.OneToOneField(related_name='school_administrator', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
