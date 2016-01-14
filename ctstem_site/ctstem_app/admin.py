from django.contrib import admin
from ctstem_app import models

# Register your models here.

admin.site.register(models.Administrator)
admin.site.register(models.Assessment)
admin.site.register(models.AssessmentQuestion)
admin.site.register(models.AssessmentStep)
admin.site.register(models.Lesson)
admin.site.register(models.LessonQuestion)
admin.site.register(models.Standard)
admin.site.register(models.Category)
admin.site.register(models.Subcategory)
admin.site.register(models.Question)
admin.site.register(models.Researcher)
admin.site.register(models.School)
admin.site.register(models.Section)
admin.site.register(models.Student)
admin.site.register(models.Subject)
admin.site.register(models.Teacher)
