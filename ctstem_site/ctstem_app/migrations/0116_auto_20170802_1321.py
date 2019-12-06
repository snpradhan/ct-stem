# -*- coding: utf-8 -*-


from django.db import models, migrations

def forward(apps, schema_editor):
    Curricula = apps.get_model("ctstem_app", "Curriculum")
    for curriculum in Curricula.objects.all():
        curriculum.authors.add(curriculum.author)

class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0115_curriculum_authors'),
    ]

    operations = [
      migrations.RunPython(forward)
    ]
