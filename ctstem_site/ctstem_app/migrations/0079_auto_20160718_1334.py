# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0078_auto_20160615_1525'),
    ]

    operations = [
        migrations.CreateModel(
            name='System',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.AlterField(
            model_name='assignment',
            name='curriculum',
            field=models.ForeignKey(related_name='assignments', to='ctstem_app.Curriculum', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='curriculum',
            name='compatible_with',
            field=models.ManyToManyField(help_text=b'Select one or more compatible systems', to='ctstem_app.System', null=True, blank=True),
        ),
    ]
