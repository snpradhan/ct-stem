# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0125_question_research_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='research_category',
            field=models.ForeignKey(related_name='questions', on_delete=django.db.models.deletion.SET_NULL, to='ctstem_app.ResearchCategory', null=True),
        ),
    ]
