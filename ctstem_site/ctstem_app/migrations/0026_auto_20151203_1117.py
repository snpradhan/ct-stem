# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0025_auto_20151130_1015'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assigned_date', models.DateTimeField(auto_now_add=True)),
                ('due_date', models.DateTimeField(null=True)),
                ('assessment', models.ForeignKey(to='ctstem_app.Assessment')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('joined_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text=b'Group Title', max_length=255)),
                ('time', models.CharField(max_length=256)),
                ('description', models.TextField(null=True)),
                ('assignments', models.ManyToManyField(related_name='assigned_to', null=True, through='ctstem_app.Assignment', to='ctstem_app.Assessment', blank=True)),
                ('members', models.ManyToManyField(related_name='member_of', null=True, through='ctstem_app.Membership', to='ctstem_app.Student', blank=True)),
                ('subject', models.ForeignKey(to='ctstem_app.Subject')),
                ('teacher', models.ForeignKey(to='ctstem_app.Teacher')),
            ],
        ),
        migrations.AddField(
            model_name='membership',
            name='group',
            field=models.ForeignKey(related_name='group_members', to='ctstem_app.UserGroup'),
        ),
        migrations.AddField(
            model_name='membership',
            name='student',
            field=models.ForeignKey(to='ctstem_app.Student'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='group',
            field=models.ForeignKey(related_name='group_assignments', to='ctstem_app.UserGroup'),
        ),
    ]
