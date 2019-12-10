# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0052_auto_20160211_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculumquestion',
            name='question',
            field=models.ForeignKey(related_name='curriculum_question', to='ctstem_app.Question', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='step',
            name='curriculum',
            field=models.ForeignKey(related_name='steps', to='ctstem_app.Curriculum', on_delete=models.CASCADE),
        ),
    ]
