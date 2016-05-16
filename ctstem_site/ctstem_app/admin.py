from django.contrib import admin
from ctstem_app import models

# Register your models here.

admin.site.register(models.Administrator)
admin.site.register(models.Curriculum)
admin.site.register(models.CurriculumQuestion)
admin.site.register(models.Step)
admin.site.register(models.Standard)
admin.site.register(models.Category)
admin.site.register(models.Subcategory)
admin.site.register(models.Question)
admin.site.register(models.Researcher)
admin.site.register(models.School)
admin.site.register(models.Student)
admin.site.register(models.Subject)
admin.site.register(models.Teacher)
