# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0062_auto_20160415_1646'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='category',
            name='order',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='questionfeedback',
            name='feedback',
            field=models.TextField(help_text=b'Enter Feedback', null=True, blank=True),
        ),
    ]
