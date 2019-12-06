# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0175_auto_20191018_1518'),
    ]

    operations = [
      migrations.RunSQL("UPDATE ctstem_app_curriculum SET curriculum_type = 'A' WHERE curriculum_type = 'S';"),

    ]
