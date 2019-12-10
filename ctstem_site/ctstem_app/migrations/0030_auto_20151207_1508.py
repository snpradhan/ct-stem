# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0029_auto_20151207_1101'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentStepResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assessment_step', models.ForeignKey(to='ctstem_app.AssessmentStep', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('response', models.TextField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('assessment_question', models.ForeignKey(to='ctstem_app.AssessmentQuestion', on_delete=models.CASCADE)),
                ('step_response', models.ForeignKey(to='ctstem_app.AssignmentStepResponse', on_delete=models.CASCADE)),
            ],
        ),
        migrations.RemoveField(
            model_name='assignmentresponse',
            name='assessment_question',
        ),
        migrations.RemoveField(
            model_name='assignmentresponse',
            name='assessment_step',
        ),
        migrations.RemoveField(
            model_name='assignmentresponse',
            name='instance',
        ),
        migrations.AlterUniqueTogether(
            name='assignmentinstance',
            unique_together=set([('assignment', 'student')]),
        ),
        migrations.DeleteModel(
            name='AssignmentResponse',
        ),
        migrations.AddField(
            model_name='assignmentstepresponse',
            name='instance',
            field=models.ForeignKey(to='ctstem_app.AssignmentInstance', on_delete=models.CASCADE),
        ),
    ]
