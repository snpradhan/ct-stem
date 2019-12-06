# -*- coding: utf-8 -*-


from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0044_auto_20160114_1340'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(null=True)),
                ('url', models.URLField(max_length=500, null=True, blank=True)),
                ('image', models.ImageField(upload_to=ctstem_app.models.upload_file_to)),
            ],
        ),
        migrations.CreateModel(
            name='TeamRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='team',
            name='role',
            field=models.ForeignKey(to='ctstem_app.TeamRole'),
        ),
    ]
