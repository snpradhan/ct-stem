# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0043_auto_20160114_1330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subcategory',
            name='category',
            field=smart_selects.db_fields.ChainedForeignKey(chained_model_field=b'standard', to='ctstem_app.Category', chained_field=b'standard', auto_choose=True),
        ),
    ]
