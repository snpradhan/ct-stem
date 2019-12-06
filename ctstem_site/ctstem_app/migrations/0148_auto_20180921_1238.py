# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0147_remove_assignment_release'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='assigned_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
