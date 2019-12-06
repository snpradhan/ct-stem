# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0138_auto_20180710_1628'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupInvitee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(help_text=b'Email', max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='title',
            field=models.CharField(help_text=b'Class Title. Eg. Physics Section A', max_length=255),
        ),
        migrations.AddField(
            model_name='groupinvitee',
            name='group',
            field=models.ForeignKey(related_name='groups', to='ctstem_app.UserGroup'),
        ),
    ]
