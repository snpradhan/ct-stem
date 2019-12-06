# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0034_auto_20160105_1527'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Standard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Taxonomy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=256)),
                ('code', models.CharField(max_length=256, null=True)),
                ('description', models.CharField(max_length=256, null=True)),
                ('link', models.URLField(max_length=500, null=True)),
                ('category', models.ForeignKey(related_name='taxonomy', to='ctstem_app.Category')),
            ],
        ),
        migrations.RemoveField(
            model_name='assessment',
            name='ct_stem_practices',
        ),
        migrations.RemoveField(
            model_name='assessment',
            name='ngss_standards',
        ),
        migrations.AddField(
            model_name='category',
            name='standard',
            field=models.ForeignKey(related_name='category', to='ctstem_app.Standard'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='taxonomy',
            field=models.ManyToManyField(to='ctstem_app.Taxonomy'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='taxonomy',
            field=models.ManyToManyField(to='ctstem_app.Taxonomy'),
        ),
    ]
