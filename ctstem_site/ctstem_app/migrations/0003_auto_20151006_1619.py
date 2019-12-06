# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0002_auto_20151005_1421'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='questions',
        ),
        migrations.AlterField(
            model_name='administrator',
            name='user',
            field=models.OneToOneField(related_name='administrator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='researcher',
            name='teachers',
            field=models.ManyToManyField(to='ctstem_app.Teacher', blank=True),
        ),
        migrations.AlterField(
            model_name='researcher',
            name='user',
            field=models.OneToOneField(related_name='researcher', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='student',
            name='user',
            field=models.OneToOneField(related_name='student', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='students',
            field=models.ManyToManyField(to='ctstem_app.Student', blank=True),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='user',
            field=models.OneToOneField(related_name='teacher', to=settings.AUTH_USER_MODEL),
        ),
    ]
