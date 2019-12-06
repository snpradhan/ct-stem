# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0118_auto_20170803_1131'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentNotes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.TextField(null=True, blank=True)),
                ('instance', models.OneToOneField(related_name='notes', to='ctstem_app.AssignmentInstance')),
            ],
        ),
    ]
