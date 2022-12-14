from django.urls import path, re_path

from . import views


app_name = 'poly_crud'
urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('administrator/', views.administrator, name='administrator'),
    path('treatments/', views.treatments, name='treatments'),
    re_path(r'^treatments/(?P<card_no>[А-Я]{2}\d{4}[А-Я]{1})/', views.tr_patients, name='tr_patients'),
    path('treatment/edit/<int:id>/', views.edit_treatment, name='edit_treatment'),
    re_path(r'^treatment/add/(?P<card_no>[А-Я]{2}\d{4}[А-Я]{1})/', views.add_treatment, name='add_treatment'),
    path('allergies/', views.allergies, name='allergies'),
    path('allergy/edit/<int:id>/', views.edit_allergy, name='edit_allergy'),
    path('allergy/add/', views.add_allergy, name='add_allergy'),
    path('specialties/', views.specialties, name='specialties'),
    re_path(r'^speciality/edit/(?P<name>[А-Я]*[а-я]*)/', views.edit_speciality, name='edit_speciality'),
    path('speciality/add/', views.add_speciality, name='add_speciality'),
    path('drags/', views.drags, name='drags'),
    path('drag/edit/<int:id>/', views.edit_drag, name='edit_drag'),
    path('drag/add/', views.add_drag, name='add_drag'),
    path('doctors/', views.doctors, name='doctors'),
    path('doctor/edit/<int:id>/', views.edit_doctor, name='edit_doctor'),
    path('doctor/add/', views.add_doctor, name='add_doctor'),
    path('patients/', views.patients, name='patients'),
    re_path(r'^patient/edit/(?P<card_no>[А-Я]{2}\d{4}[А-Я]{1})/', views.edit_patient, name='edit_patient'),
    path('patient/add/', views.add_patient, name='add_patient'),
]