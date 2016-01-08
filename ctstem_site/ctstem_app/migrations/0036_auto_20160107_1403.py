# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0035_auto_20160107_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxonomy',
            name='standard',
            field=models.ForeignKey(related_name='taxonomy', default=1, to='ctstem_app.Standard'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='taxonomy',
            name='category',
            field=smart_selects.db_fields.ChainedForeignKey(chained_model_field=b'standard', to='ctstem_app.Category', chained_field=b'standard', auto_choose=True),
        ),
        migrations.AlterField(
            model_name='taxonomy',
            name='code',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='taxonomy',
            name='description',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='taxonomy',
            name='link',
            field=models.URLField(max_length=500, null=True, blank=True),
        ),
    ]
