# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Administrator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=256)),
                ('time', models.CharField(max_length=256, null=True)),
                ('overview', models.TextField()),
                ('status', models.CharField(default=b'D', max_length=1, choices=[('D', 'Draft'), ('P', 'Published')])),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(related_name='assessment_author', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='AssessmentQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssessmentStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=256, null=True)),
                ('order', models.IntegerField(null=True)),
                ('content', models.TextField()),
                ('assessment_id', models.ForeignKey(to='ctstem_app.Assessment')),
            ],
        ),
        migrations.CreateModel(
            name='CTStemPractice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(max_length=2, choices=[('DA', 'Data Analysis'), ('MS', 'Modeling & Simulation'), ('CPS', 'Computational Problem Solving'), ('ST', 'Systems Thinking')])),
                ('title', models.CharField(max_length=256, null=True)),
                ('overview', models.TextField()),
                ('order', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=256)),
                ('time', models.CharField(max_length=256, null=True)),
                ('purpose', models.TextField()),
                ('overview', models.TextField()),
                ('content', models.TextField()),
                ('status', models.CharField(default=b'D', max_length=1, choices=[('D', 'Draft'), ('P', 'Published')])),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(related_name='lesson_author', to=settings.AUTH_USER_MODEL)),
                ('ct_stem_practices', models.ManyToManyField(to='ctstem_app.CTStemPractice')),
                ('modified_by', models.ForeignKey(related_name='lesson_modifier', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='LessonQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(null=True)),
                ('lesson', models.ForeignKey(to='ctstem_app.Lesson')),
            ],
        ),
        migrations.CreateModel(
            name='NGSSStandard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question_text', models.TextField()),
                ('answer_field_type', models.CharField(max_length=2, choices=[('TA', 'Text Area'), ('TF', 'Text Field'), ('SB', 'Slider Bar'), ('DD', 'Drop Down'), ('MS', 'Multi-Select'), ('MC', 'Multiple Choice')])),
                ('options', models.TextField(null=True, blank=True)),
                ('answer', models.TextField(null=True, blank=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Researcher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('city', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, choices=[('PHYSICS', 'PHYSICS'), ('BIOLOGY', 'BIOLOGY'), ('CHEMISTRY', 'CHEMISTRY'), ('MATH', 'MATH'), ('ASTRONOMY', 'ASTRONOMY'), ('EARTH SCIENCE', 'EARTH SCIENCE'), ('BIOTECHNOLOGY', 'BIOTECHNOLOGY'), ('GENETICS', 'GENETICS'), ('PHYSIOLOGY', 'PHYSIOLOGY'), ('HUMAN ANATOMY', 'HUMAN ANATOMY'), ('ENVIRONMENTAL SCIENCE', 'ENVIRONMENTAL SCIENCE'), ('SPACE SCIENCE', 'SPACE SCIENCE'), ('FORENSIC SCIENCE', 'FORENSIC SCIENCE'), ('PHYSICAL SCIENCE', 'PHYSICAL SCIENCE'), ('NATURAL SCIENCE', 'NATURAL SCIENCE'), ('GEOLOGY', 'GEOLOGY'), ('ECOLOGY', 'ECOLOGY'), ('GENERAL SCIENCE', 'GENERAL SCIENCE')])),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('school', models.ForeignKey(to='ctstem_app.School')),
                ('students', models.ManyToManyField(to='ctstem_app.Student')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='section',
            name='students',
            field=models.ManyToManyField(to='ctstem_app.Student'),
        ),
        migrations.AddField(
            model_name='section',
            name='subject',
            field=models.ForeignKey(to='ctstem_app.Subject'),
        ),
        migrations.AddField(
            model_name='section',
            name='teacher',
            field=models.ForeignKey(to='ctstem_app.Teacher'),
        ),
        migrations.AddField(
            model_name='researcher',
            name='school',
            field=models.ForeignKey(to='ctstem_app.School'),
        ),
        migrations.AddField(
            model_name='researcher',
            name='teachers',
            field=models.ManyToManyField(to='ctstem_app.Teacher'),
        ),
        migrations.AddField(
            model_name='researcher',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lessonquestion',
            name='question',
            field=models.ForeignKey(to='ctstem_app.Question'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='ngss_standards',
            field=models.ManyToManyField(to='ctstem_app.NGSSStandard'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='questions',
            field=models.ManyToManyField(to='ctstem_app.Question', through='ctstem_app.LessonQuestion'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='subject',
            field=models.ManyToManyField(to='ctstem_app.Subject'),
        ),
        migrations.AddField(
            model_name='assessmentstep',
            name='questions',
            field=models.ManyToManyField(to='ctstem_app.Question', through='ctstem_app.AssessmentQuestion'),
        ),
        migrations.AddField(
            model_name='assessmentquestion',
            name='assessment_step',
            field=models.ForeignKey(to='ctstem_app.AssessmentStep'),
        ),
        migrations.AddField(
            model_name='assessmentquestion',
            name='question',
            field=models.ForeignKey(to='ctstem_app.Question'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='ct_stem_practices',
            field=models.ManyToManyField(to='ctstem_app.CTStemPractice'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='modified_by',
            field=models.ForeignKey(related_name='assessment_modifier', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assessment',
            name='ngss_standards',
            field=models.ManyToManyField(to='ctstem_app.NGSSStandard'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='subject',
            field=models.ManyToManyField(to='ctstem_app.Subject'),
        ),
    ]
