# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0135_auto_20180314_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='iframestate',
            name='url',
            field=models.URLField(default='http://cnn.com', max_length=1600),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='iframestate',
            unique_together=set([('instance', 'iframe_id', 'url')]),
        ),
    ]
