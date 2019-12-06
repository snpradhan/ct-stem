# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0150_usergroup_coteachers'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='membership',
            options={'ordering': ('student__user__first_name', 'student__user__last_name')},
        ),
        migrations.AlterModelOptions(
            name='teacher',
            options={'ordering': ['user__first_name', 'user__last_name']},
        ),
        migrations.RemoveField(
            model_name='usergroup',
            name='coteachers',
        ),
        migrations.AddField(
            model_name='usergroup',
            name='shared_with',
            field=models.ManyToManyField(help_text=b'Select teachers to share this class with.', to='ctstem_app.Teacher', null=True, blank=True),
        ),
    ]
