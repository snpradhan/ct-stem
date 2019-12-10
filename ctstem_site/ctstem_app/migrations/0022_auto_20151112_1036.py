# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0021_auto_20151111_1204'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=256)),
                ('order', models.IntegerField(null=True)),
                ('content', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='questions',
        ),
        migrations.RemoveField(
            model_name='lessonquestion',
            name='lesson',
        ),
        migrations.AddField(
            model_name='lessonactivity',
            name='lesson',
            field=models.ForeignKey(to='ctstem_app.Lesson', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='lessonactivity',
            name='questions',
            field=models.ManyToManyField(to='ctstem_app.Question', through='ctstem_app.LessonQuestion', blank=True),
        ),
        migrations.AddField(
            model_name='lessonquestion',
            name='lesson_activity',
            field=models.ForeignKey(to='ctstem_app.LessonActivity', null=True, on_delete=models.CASCADE),
        ),
    ]
