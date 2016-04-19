# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0060_bookmarkedcurriculum'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('feedback', models.TextField(null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('response', models.ForeignKey(to='ctstem_app.QuestionResponse')),
            ],
        ),
        migrations.AlterField(
            model_name='bookmarkedcurriculum',
            name='curriculum',
            field=models.ForeignKey(related_name='bookmarked', to='ctstem_app.Curriculum'),
        ),
    ]
