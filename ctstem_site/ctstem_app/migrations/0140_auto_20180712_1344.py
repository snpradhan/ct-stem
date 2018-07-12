# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0139_auto_20180712_1335'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='groupinvitee',
            unique_together=set([('group', 'email')]),
        ),
    ]
