# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-04-30 11:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctstem_app', '0190_auto_20200428_1332'),
    ]

    operations = [
      migrations.RunSQL('INSERT INTO ctstem_app_curriculumcollaborator(curriculum_id, user_id, privilege, "order") \
                         SELECT c.unit_id, cc1.user_id, min(cc1.privilege), min(cc1."order") \
                         FROM ctstem_app_curriculumcollaborator cc1 JOIN ctstem_app_curriculum c ON cc1.curriculum_id = c.id \
                         WHERE c.unit_id IS NOT NULL AND not exists (SELECT 1 \
                                                                     FROM ctstem_app_curriculumcollaborator cc2 \
                                                                     WHERE cc2.curriculum_id = c.unit_id AND cc2.user_id = cc1.user_id) \
                         GROUP BY c.unit_id, cc1.user_id; \
                        '),
      migrations.RunSQL('UPDATE ctstem_app_curriculumcollaborator \
                         SET privilege = \'E\' \
                         WHERE id IN (SELECT cc2.id \
                                          FROM ctstem_app_curriculumcollaborator cc2 JOIN \
                                               (SELECT DISTINCT c.unit_id AS curriculum_id, cc3.user_id AS user_id \
                                                FROM ctstem_app_curriculumcollaborator cc3 JOIN ctstem_app_curriculum c ON cc3.curriculum_id = c.id \
                                                WHERE c.unit_id IS NOT NULL AND EXISTS (SELECT 1 \
                                                                                        FROM ctstem_app_curriculumcollaborator cc4 \
                                                                                        WHERE cc4.curriculum_id = c.unit_id AND \
                                                                                              cc4.user_id = cc3.user_id AND \
                                                                                              cc4.privilege != cc3.privilege) \
                                               ) tm ON cc2.curriculum_id = tm.curriculum_id AND cc2.user_id = tm.user_id \
                                          ); \
                        '),
      migrations.RunSQL('DELETE FROM ctstem_app_curriculumcollaborator cc \
                         WHERE EXISTS (SELECT 1 \
                                       FROM ctstem_app_curriculum c \
                                       WHERE c.id = cc.curriculum_id AND c.unit_id IS NOT NULL); \
                        '),
    ]
