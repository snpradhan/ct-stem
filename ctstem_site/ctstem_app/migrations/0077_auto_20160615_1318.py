# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0076_auto_20160615_0958'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignmentinstance',
            name='teammates',
            field=models.ManyToManyField(to='ctstem_app.Student', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='assignmentinstance',
            name='student',
            field=models.ForeignKey(related_name='instance', to='ctstem_app.Student', on_delete=models.CASCADE),
        ),
    ]
