from django.urls import path

from . import views

app_name = "detect"

urlpatterns = [
    path('', views.home_page, name="home"),
    path('theory/', views.theory1, name="theory_list"),
    path('theory/1/', views.theory1, name="theory1"),
    path('theory/2/', views.theory2, name="theory2"),
    path('theory/3/', views.theory3, name="theory3"),
    path('laboratory/', views.lab1_example, name="lab1_example"),
    path('laboratory/1/', views.laboratory1, name="laboratory1"),
    path('laboratory/2/', views.laboratory2, name="laboratory2"),
    path('laboratory/3/', views.laboratory3, name="laboratory3"),
    path('laboratory/4/', views.laboratory4, name="laboratory4"),
    path('test/', views.final_test, name="final_test"),
    path('result_is_db/', views.result_is_db, name="result"),
]
