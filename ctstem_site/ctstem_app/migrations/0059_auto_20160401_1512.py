# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0058_auto_20160309_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignmentinstance',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 1, 20, 12, 35, 494614, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='teacher',
            field=models.ForeignKey(related_name='groups', to='ctstem_app.Teacher'),
        ),
    ]
