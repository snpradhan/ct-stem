from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^lessons/$', views.lessons, name='lessons'),
    url(r'^about-us/$', views.about_us, name='about_us'),

]
