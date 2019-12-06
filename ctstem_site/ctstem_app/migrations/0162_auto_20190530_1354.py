# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0161_auto_20190522_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='authors',
            field=models.ManyToManyField(help_text=b'Select authors for this curriculum.', related_name='curriculum_authors', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='status',
            field=models.CharField(default=b'D', max_length=1, choices=[('D', 'Private'), ('P', 'Public'), ('A', 'Archived')]),
        ),
    ]
