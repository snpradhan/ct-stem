# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0087_auto_20160812_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='consent',
            field=models.CharField(default=b'U', max_length=1, choices=[('A', 'I Agree'), ('D', 'I Disagree')]),
        ),
    ]
