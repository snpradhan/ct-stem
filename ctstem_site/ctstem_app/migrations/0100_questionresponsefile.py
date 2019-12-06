# -*- coding: utf-8 -*-


from django.db import models, migrations
import ctstem_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0099_auto_20170215_1336'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionResponseFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=ctstem_app.models.upload_file_to, blank=True)),
                ('question_response', models.ForeignKey(related_name='response_file', to='ctstem_app.QuestionResponse')),
            ],
        ),
    ]
