# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0144_subject_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroup',
            name='title',
            field=models.CharField(help_text=b'Class Title. Eg. Physics Section A', max_length=50),
        ),
    ]
