# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0132_auto_20171122_1101'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='researchcategory',
            options={'ordering': ['category']},
        ),
        migrations.AddField(
            model_name='assignment',
            name='lock_on_completion',
            field=models.BooleanField(default=False),
        ),
    ]
