# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0134_auto_20180314_1201'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='iframestate',
            unique_together=set([('instance', 'iframe_id')]),
        ),
        migrations.RemoveField(
            model_name='iframestate',
            name='step',
        ),
    ]
