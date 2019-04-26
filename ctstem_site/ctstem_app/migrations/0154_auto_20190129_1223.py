# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0153_usergroup_icon'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='groupinvitee',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='groupinvitee',
            name='group',
        ),
        migrations.DeleteModel(
            name='GroupInvitee',
        ),
    ]
