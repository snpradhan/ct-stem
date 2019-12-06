# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0041_remove_publication_publication_affiliation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assessmentstep',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='lessonactivity',
            options={'ordering': ['order']},
        ),
    ]
