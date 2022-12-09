from django.urls import path, re_path

from . import views


app_name = 'poly_crud'
urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('administrator/', views.administrator, name='administrator'),
    path('patients/', views.patients, name='patients'),
    re_path(r'^treatments/(?P<card_no>[А-Я]{2}\d{4}[А-Я]{1})/', views.treatments, name='card_no'),
    path('treatment/edit/<int:id>/', views.edit_treatment, name='edit_treatment'),
    re_path(r'^treatment/add/(?P<card_no>[А-Я]{2}\d{4}[А-Я]{1})/', views.add_treatment, name='add_treatment'),
]