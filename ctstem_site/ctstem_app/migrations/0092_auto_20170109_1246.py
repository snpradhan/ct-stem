# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0091_auto_20161103_1126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='assigned_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 1, 9, 12, 46, 47, 1231)),
        ),
        migrations.AlterField(
            model_name='assignmentinstance',
            name='teammates',
            field=models.ManyToManyField(help_text=b'On Windows use Ctrl+Click to make multiple selection.  On a Mac use Cmd+Click to make multiple selection', to='ctstem_app.Student', null=True, blank=True),
        ),
    ]
