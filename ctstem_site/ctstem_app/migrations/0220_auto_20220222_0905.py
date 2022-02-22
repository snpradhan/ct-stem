# Generated by Django 2.2.27 on 2022-02-22 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0219_auto_20220222_0749'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publication',
            old_name='pages',
            new_name='from_page',
        ),
        migrations.RenameField(
            model_name='publication',
            old_name='publisher',
            new_name='journal',
        ),
        migrations.AddField(
            model_name='publication',
            name='issue',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='publication',
            name='to_page',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
