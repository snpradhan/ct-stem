# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0133_auto_20171208_1544'),
    ]

    operations = [
        migrations.CreateModel(
            name='IframeState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('iframe_id', models.CharField(max_length=255)),
                ('state', models.TextField(null=True, blank=True)),
                ('instance', models.ForeignKey(to='ctstem_app.AssignmentInstance', on_delete=models.CASCADE)),
                ('step', models.ForeignKey(to='ctstem_app.Step', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='iframestate',
            unique_together=set([('instance', 'step', 'iframe_id')]),
        ),
    ]
