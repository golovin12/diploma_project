from django.urls import path, re_path

from . import views

app_name = "detect"

urlpatterns = [
    path('', views.home_page, name="home"),
    path('theory/', views.theory1, name="theory_list"),
    path('theory/1/', views.theory1, name="theory1"),
    path('theory/2/', views.theory2, name="theory2"),
    path('theory/3/', views.theory3, name="theory3"),
    path('laborathory/', views.lab1_example, name="lab1_example"),
    path('laborathory/1/<str:modulation>/', views.laboratory1, name="laboratory1"),
    path('laborathory/2/', views.laborathory2, name="laboratory2"),
    path('laborathory/3/', views.laborathory3, name="laboratory3"),
    path('laborathory/4/', views.laborathory4, name="laboratory4"),
    path('test/', views.tests, name="test"),
    path('result_is_db/', views.result_is_db, name="result"),
]
