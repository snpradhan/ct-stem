# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0158_auto_20190514_1050'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='questionfeedback',
            options={'ordering': ('response__curriculum_question__order',)},
        ),
        migrations.AlterModelOptions(
            name='stepfeedback',
            options={'ordering': ('step_response__step__order',)},
        ),
    ]
