# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0166_auto_20190702_1215'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='feature_rank',
            field=models.IntegerField(help_text=b'Order in the feature pool', null=True, blank=True),
        ),
    ]
