from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^assessments/$', views.assessments, name='assessments'),
    url(r'^assessment/new/$', views.assessment, name='newAssessment'),
    url(r'^assessment/(?P<id>[\d]+)/$', views.assessment, name='assessment'),
    url(r'^assessment/delete/(?P<id>[\d]+)/$', views.deleteAssessment, name='deleteAssessment'),
    url(r'^publication/(?P<slug>[\w-]+)/$', views.publication, name='publication'),
    url(r'^publication/delete/(?P<slug>[\w-]+)/$', views.deletePublication, name='deletePublication'),
    url(r'^publication/new/$', views.publication, name='newPublication'),
    url(r'^publications/$', views.publications, name='publications'),
    url(r'^lessons/$', views.lessons, name='lessons'),
    url(r'^partners/$', views.partners, name='partners'),
    url(r'^jobs/$', views.notimplemented, name='jobs'),
    url(r'^events/$', views.notimplemented, name='events'),
    url(r'^publications/$', views.notimplemented, name='publications'),
    url(r'^about-us/$', views.about_us, name='about_us'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^user/(?P<id>[\d]+)/$', views.userProfile, name='userProfile'),
    url(r'^lesson/(?P<id>[\d]+)/$', views.lesson, name='lesson'),
    url(r'^lesson/new/$', views.lesson, name='newLesson'),
    url(r'^lesson/preview/(?P<id>[\d]+)/$', views.previewLesson, name='previewLesson'),
    url(r'^lesson/delete/(?P<id>[\d]+)/$', views.deleteLesson, name='deleteLesson'),
    url(r'^assessment/preview/(?P<id>[\d]+)/$', views.previewAssessment, name='previewAssessment'),
    url(r'^taxonomy/$', views.taxonomy, name='taxonomy'),
    url(r'^taxonomy/ngss_standard/$', views.ngss_standard, name='ngss_standard'),
    url(r'^taxonomy/ctstem_practice/$', views.ctstem_practice, name='ctstem_practice'),
    url(r'^users/(?P<role>[a-zA-Z0-9]+)/$', views.users, name='users'),
    url(r'^question/new/$', views.question, name='newQuestion'),
    url(r'^question/(?P<id>[\d]+)/$', views.question, name='question'),


]
