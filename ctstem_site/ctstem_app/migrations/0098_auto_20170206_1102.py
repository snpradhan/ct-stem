# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0097_auto_20170203_1208'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trainingrequest',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='trainingrequest',
            name='requester_role',
        ),
        migrations.AddField(
            model_name='trainingrequest',
            name='subject',
            field=models.CharField(default='Algebra', help_text=b'Subject', max_length=255),
            preserve_default=False,
        ),
    ]
