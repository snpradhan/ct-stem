# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0028_remove_usergroup_assignments'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=255, choices=[('N', 'New'), ('P', 'In Progress'), ('S', 'Submitted'), ('F', 'Feedback Ready')])),
                ('last_step', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='AssignmentResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('response', models.TextField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('assessment_question', models.ForeignKey(to='ctstem_app.AssessmentQuestion', on_delete=models.CASCADE)),
                ('assessment_step', models.ForeignKey(to='ctstem_app.AssessmentStep', on_delete=models.CASCADE)),
                ('instance', models.ForeignKey(to='ctstem_app.AssignmentInstance', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AlterField(
            model_name='assignment',
            name='group',
            field=models.ForeignKey(related_name='assignments', to='ctstem_app.UserGroup', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='assignmentinstance',
            name='assignment',
            field=models.ForeignKey(to='ctstem_app.Assignment', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='assignmentinstance',
            name='student',
            field=models.ForeignKey(to='ctstem_app.Student', on_delete=models.CASCADE),
        ),
    ]
