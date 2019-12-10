# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0137_auto_20180315_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroup',
            name='subject',
            field=models.ForeignKey(blank=True, to='ctstem_app.Subject', null=True, on_delete=models.SET_NULL),
        ),
    ]
