from django.shortcuts import render
from django.http import HttpResponse
from ctstem_app import models

# Create your views here.

def index(request):
  lessons = models.Lesson.objects.order_by('id')
  context = {'lessons': lessons}
  return render(request, 'ctstem_app/base.html', context)

def lessons(request):
  lessons = models.Lesson.objects.order_by('id')
  context = {'lessons': lessons}
  return render(request, 'ctstem_app/lessons.html', context)

def about_us(request):
  return render(request, 'ctstem_app/about_us.html')

