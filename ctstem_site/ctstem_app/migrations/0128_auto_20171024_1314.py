# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0127_auto_20171024_1312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='research_category',
            field=models.ForeignKey(related_name='questions', on_delete=models.SET_NULL, blank=True, to='ctstem_app.ResearchCategory', null=True),
        ),
    ]
