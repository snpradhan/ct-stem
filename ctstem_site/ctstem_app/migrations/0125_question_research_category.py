# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0124_researchcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='research_category',
            field=models.ForeignKey(related_name='questions', to='ctstem_app.ResearchCategory', null=True, on_delete=models.SET_NULL),
        ),
    ]
