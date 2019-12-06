# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0107_auto_20170414_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='student',
            field=models.ForeignKey(related_name='student_membership', to='ctstem_app.Student'),
        ),
    ]
