"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/settings/
For the full list of settings and their values, see
    https://docs.djangoproject.com/en/6.0/ref/settings/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from cleaning.admin import admin_site
from .health import health_check

urlpatterns = [
    path('admin/', admin_site.urls),
    path('health/', health_check, name='health'),
    path('', include('cleaning.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)