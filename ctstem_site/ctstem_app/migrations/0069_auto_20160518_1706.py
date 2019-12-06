# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0068_trainingrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingrequest',
            name='requester_role',
            field=models.CharField(help_text=b'I am:', max_length=255, choices=[('', 'I am:'), ('T', 'Teacher'), ('R', 'Researcher'), ('A', 'School Administrator'), ('O', 'Other')]),
        ),
    ]
