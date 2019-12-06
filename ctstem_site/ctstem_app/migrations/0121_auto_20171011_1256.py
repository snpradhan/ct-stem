# -*- coding: utf-8 -*-


from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0120_curriculumquestion_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionresponse',
            name='response',
            field=ckeditor.fields.RichTextField(null=True, blank=True),
        ),
    ]
