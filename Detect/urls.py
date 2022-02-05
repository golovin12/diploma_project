"""Detect URL Configuration

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
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from Detect_for_test import views

urlpatterns = [
    re_path(r'^theory/1/', views.theory1),
    re_path(r'^theory/2/', views.theory2),
    re_path(r'^theory/3/', views.theory3),
    re_path(r'^theory/', views.theory1),
    re_path(r'^laborathory/1/', views.laborathory1),
    re_path(r'^laborathory/2/', views.laborathory2),
    re_path(r'^laborathory/3/', views.laborathory3),
    re_path(r'^laborathory/4/', views.laborathory4),
    re_path(r'^laborathory/', views.laborathory1),
    re_path(r'^test/', views.tests),
    re_path(r'^shablon/', views.shablon),
    path('result_is_db/', views.result_is_db),
    re_path(r'^', views.glavnaya, name="home"),
]

handler500 = views.m500
handler410 = views.m410
handler405 = views.m405
handler404 = views.m404
handler403 = views.m403
handler400 = views.m400
handler304 = views.m304
