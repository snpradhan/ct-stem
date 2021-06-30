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
from django.urls import path, re_path
from django.contrib import admin
from ckeditor_uploader import views
from ctstem_app.views import SchoolAutocomplete
from django.conf.urls.static import static

urlpatterns = [
    path('', include('ctstem_app.urls', namespace="ctstem")),
    path('admin/', admin.site.urls),
    path('password_reset/', include('password_reset.urls')),
    path('ckeditor/upload/', views.upload, name='ckeditor_upload'),
    path('ckeditor/browse/', views.browse, name='ckeditor_browse'),
    path('chaining/', include('smart_selects.urls')),
    path('school-autocomplete/', SchoolAutocomplete.as_view(), name='school-autocomplete',),
    path('auth/', include('social_django.urls', namespace='social')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
