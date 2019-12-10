# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0049_standard_primary'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subcategory',
            name='standard',
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='category',
            field=models.ForeignKey(related_name='subcategory', to='ctstem_app.Category', on_delete=models.CASCADE),
        ),
    ]
