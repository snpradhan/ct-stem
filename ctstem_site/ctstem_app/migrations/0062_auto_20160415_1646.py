# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0061_auto_20160415_1538'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('instance', models.ForeignKey(to='ctstem_app.AssignmentInstance', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('feedback', models.TextField(null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('response', models.ForeignKey(to='ctstem_app.QuestionResponse', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='StepFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assignment_feedback', models.ForeignKey(to='ctstem_app.AssignmentFeedback', on_delete=models.CASCADE)),
                ('step_response', models.ForeignKey(to='ctstem_app.AssignmentStepResponse', on_delete=models.CASCADE)),
            ],
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='response',
        ),
        migrations.DeleteModel(
            name='Feedback',
        ),
        migrations.AddField(
            model_name='questionfeedback',
            name='step_feedback',
            field=models.ForeignKey(to='ctstem_app.StepFeedback', on_delete=models.CASCADE),
        ),
    ]
