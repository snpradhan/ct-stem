# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0042_auto_20160113_1106'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=256)),
                ('code', models.CharField(max_length=256, null=True, blank=True)),
                ('description', models.CharField(max_length=256, null=True, blank=True)),
                ('link', models.URLField(max_length=500, null=True, blank=True)),
                ('category', smart_selects.db_fields.ChainedForeignKey(chained_model_field=b'standard', to='ctstem_app.Category', chained_field=b'subcategory', auto_choose=True)),
                ('standard', models.ForeignKey(related_name='subcategory', to='ctstem_app.Standard')),
            ],
        ),
        migrations.RemoveField(
            model_name='taxonomy',
            name='category',
        ),
        migrations.RemoveField(
            model_name='taxonomy',
            name='standard',
        ),
        migrations.AlterField(
            model_name='assessment',
            name='taxonomy',
            field=models.ManyToManyField(to='ctstem_app.Subcategory'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='taxonomy',
            field=models.ManyToManyField(to='ctstem_app.Subcategory'),
        ),
        migrations.DeleteModel(
            name='Taxonomy',
        ),
    ]
