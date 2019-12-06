# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0098_auto_20170206_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingrequest',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 15, 19, 36, 13, 471412, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='trainingrequest',
            name='email',
            field=models.EmailField(help_text=b'Email', max_length=255),
        ),
    ]
