# -*- coding: utf-8 -*-


from django.db import models, migrations
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0072_auto_20160602_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='subject',
            field=models.ManyToManyField(to='ctstem_app.Subject', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='options',
            field=models.TextField(help_text=b'For dropdown, multi-select and multiple choice questions provide one option per line', null=True, blank=True),
        ),
    ]
