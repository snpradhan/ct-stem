# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0136_auto_20180315_1321'),
    ]

    operations = [
        migrations.RenameField(
            model_name='iframestate',
            old_name='url',
            new_name='iframe_url',
        ),
        migrations.AlterUniqueTogether(
            name='iframestate',
            unique_together=set([('instance', 'iframe_id', 'iframe_url')]),
        ),
    ]
