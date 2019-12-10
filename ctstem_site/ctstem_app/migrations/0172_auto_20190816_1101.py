# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0171_auto_20190719_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='school',
            field=models.ForeignKey(related_name='teachers', to='ctstem_app.School', on_delete=models.SET_NULL),
        ),
    ]
