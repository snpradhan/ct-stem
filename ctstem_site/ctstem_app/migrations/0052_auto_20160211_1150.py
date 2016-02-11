# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ctstem_app.models
import django.db.models.deletion
from django.conf import settings
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ctstem_app', '0051_attachment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Curriculum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('curriculum_type', models.CharField(max_length=1, choices=[('L', 'Lesson Plan'), ('A', 'Assessment')])),
                ('title', models.CharField(max_length=256)),
                ('time', models.CharField(max_length=256, null=True)),
                ('level', models.TextField()),
                ('purpose', models.TextField()),
                ('overview', models.TextField()),
                ('content', ckeditor_uploader.fields.RichTextUploadingField()),
                ('teacher_notes', ckeditor_uploader.fields.RichTextUploadingField(null=True, blank=True)),
                ('status', models.CharField(default=b'D', max_length=1, choices=[('D', 'Draft'), ('P', 'Published'), ('A', 'Archived')])),
                ('version', models.IntegerField(default=1)),
                ('slug', models.SlugField(unique=True, max_length=255)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(related_name='curriculum_author', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(related_name='curriculum_modifier', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='ctstem_app.Curriculum', null=True)),
                ('subject', models.ManyToManyField(to='ctstem_app.Subject')),
                ('taxonomy', models.ManyToManyField(to='ctstem_app.Subcategory')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='CurriculumQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(null=True)),
                ('question', models.ForeignKey(to='ctstem_app.Question')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=256)),
                ('order', models.IntegerField(null=True)),
                ('content', ckeditor_uploader.fields.RichTextUploadingField()),
                ('teacher_notes', ckeditor_uploader.fields.RichTextUploadingField(null=True, blank=True)),
                ('curriculum', models.ForeignKey(to='ctstem_app.Curriculum')),
                ('questions', models.ManyToManyField(to='ctstem_app.Question', through='ctstem_app.CurriculumQuestion', blank=True)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='assessment',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='assessment',
            name='author',
        ),
        migrations.RemoveField(
            model_name='assessment',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='assessment',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='assessment',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='assessment',
            name='taxonomy',
        ),
        migrations.RemoveField(
            model_name='assessmentquestion',
            name='assessment_step',
        ),
        migrations.RemoveField(
            model_name='assessmentquestion',
            name='question',
        ),
        migrations.RemoveField(
            model_name='assessmentstep',
            name='assessment',
        ),
        migrations.RemoveField(
            model_name='assessmentstep',
            name='questions',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='author',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='taxonomy',
        ),
        migrations.RemoveField(
            model_name='lessonactivity',
            name='lesson',
        ),
        migrations.RemoveField(
            model_name='lessonactivity',
            name='questions',
        ),
        migrations.RemoveField(
            model_name='lessonquestion',
            name='lesson_activity',
        ),
        migrations.RemoveField(
            model_name='lessonquestion',
            name='question',
        ),
        migrations.RemoveField(
            model_name='assignment',
            name='assessment',
        ),
        migrations.RemoveField(
            model_name='assignmentstepresponse',
            name='assessment_step',
        ),
        migrations.RemoveField(
            model_name='attachment',
            name='lesson',
        ),
        migrations.RemoveField(
            model_name='questionresponse',
            name='assessment_question',
        ),
        migrations.AlterField(
            model_name='attachment',
            name='file_object',
            field=models.FileField(upload_to=ctstem_app.models.upload_file_to, blank=True),
        ),
        migrations.DeleteModel(
            name='Assessment',
        ),
        migrations.DeleteModel(
            name='AssessmentQuestion',
        ),
        migrations.DeleteModel(
            name='AssessmentStep',
        ),
        migrations.DeleteModel(
            name='Lesson',
        ),
        migrations.DeleteModel(
            name='LessonActivity',
        ),
        migrations.DeleteModel(
            name='LessonQuestion',
        ),
        migrations.AddField(
            model_name='curriculumquestion',
            name='step',
            field=models.ForeignKey(to='ctstem_app.Step', null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='curriculum',
            field=models.ForeignKey(default=1, to='ctstem_app.Curriculum'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='assignmentstepresponse',
            name='step',
            field=models.ForeignKey(default=1, to='ctstem_app.Step'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attachment',
            name='curriculum',
            field=models.ForeignKey(default=1, to='ctstem_app.Curriculum'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='questionresponse',
            name='curriculum_question',
            field=models.ForeignKey(default=1, to='ctstem_app.CurriculumQuestion'),
            preserve_default=False,
        ),
    ]
