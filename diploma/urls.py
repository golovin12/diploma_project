"""diploma URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('detect/', include('detect.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.static import serve
from django.urls import path, include
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('', RedirectView.as_view(url='/detect/'), name="home"),
    path('admin/', admin.site.urls),
    path('detect/', include('detect.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = views.m500
handler410 = views.m410
handler405 = views.m405
handler404 = views.m404
handler403 = views.m403
handler400 = views.m400
handler304 = views.m304
