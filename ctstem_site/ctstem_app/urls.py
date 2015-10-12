from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.notimplemented, name='home'),
    url(r'^assessments/$', views.assessments, name='assessments'),
    url(r'^assessment/new/$', views.assessment, name='newAssessment'),
    url(r'^assessment/(?P<id>[\d]+)/$', views.assessment, name='assessment'),
    url(r'^lessons/$', views.lessons, name='lessons'),
    url(r'^partners/$', views.notimplemented, name='partners'),
    url(r'^workshops/$', views.notimplemented, name='workshops'),
    url(r'^publications/$', views.notimplemented, name='publications'),
    url(r'^about-us/$', views.about_us, name='about_us'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^user/(?P<id>[\d]+)/$', views.userProfile, name='userProfile'),
    url(r'^lesson/(?P<id>[\d]+)/$', views.lesson, name='lesson'),
    url(r'^lesson/new/$', views.lesson, name='newLesson'),
    url(r'^lesson/preview/(?P<id>[\d]+)/$', views.lessonPreview, name='lessonPreview'),

]
