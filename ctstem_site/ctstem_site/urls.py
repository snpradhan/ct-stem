"""ctstem_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from ckeditor_uploader import views
from ctstem_app.views import SchoolAutocomplete
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #url(r'^tinymce/', include('tinymce.urls')),
    #url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^password_reset/', include('password_reset.urls')),
    url(r'^', include('ctstem_app.urls', namespace="ctstem")),
    url(r'^ckeditor/upload/', views.upload, name='ckeditor_upload'),
    url(r'^ckeditor/browse/', views.browse, name='ckeditor_browse'),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^school-autocomplete/$', SchoolAutocomplete.as_view(), name='school-autocomplete',),
    url(r'^auth/', include('social_django.urls', namespace='social')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

'''urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)'''
