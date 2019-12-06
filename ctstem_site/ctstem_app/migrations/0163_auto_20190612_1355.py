# -*- coding: utf-8 -*-


from django.db import models, migrations


def convert_level_to_plain_text(apps, schema_editor):
    curricula = apps.get_model('ctstem_app', 'Curriculum')
    for curriculum in curricula.objects.all():
        level = curriculum.level.replace('<p>', '').replace('</p>', '')
        curricula.objects.filter(id=curriculum.id).update(level=level)


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0162_auto_20190530_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='level',
            field=models.TextField(help_text=b'Student level', null=True, blank=True),
        ),
        migrations.RunPython(convert_level_to_plain_text),
    ]
