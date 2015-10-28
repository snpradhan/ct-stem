# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0014_publication'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publication',
            old_name='localCopy',
            new_name='local_copy',
        ),
        migrations.RenameField(
            model_name='publication',
            old_name='pubAffil',
            new_name='publication_affiliation',
        ),
        migrations.RenameField(
            model_name='publication',
            old_name='pubType',
            new_name='publication_type',
        ),
        migrations.RenameField(
            model_name='publication',
            old_name='weblink',
            new_name='url',
        ),
        migrations.AlterField(
            model_name='publication',
            name='authors',
            field=models.CharField(help_text=b'Publication Author', max_length=255),
        ),
        migrations.AlterField(
            model_name='publication',
            name='title',
            field=models.CharField(help_text=b'Publication Title', max_length=255),
        ),
        migrations.AlterField(
            model_name='publication',
            name='year',
            field=models.CharField(help_text=b'Publication Year', max_length=255),
        ),
    ]
