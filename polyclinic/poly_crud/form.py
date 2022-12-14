from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.template.context_processors import request

from poly_crud.logic import get_group, select
from poly_crud.models import *


class TreatmentForm(forms.Form):
    date_in = forms.DateField(label='Дата поступления')
    date_out = forms.DateField(label='Дата выписки', required=False)
    diagnosis = forms.CharField(label='Диагноз', required=False, empty_value=None, max_length=120)
    symptom = forms.CharField(label='Симптом', empty_value=None, max_length=120)
    id_doctor = forms.ModelChoiceField(label='Лечащий врач', queryset=None)
    card_no_patient = forms.ModelChoiceField(label='Номер карты пациента', queryset=None)
    treatment_drag = forms.ModelMultipleChoiceField(label='Прописанные лекарства',
                                                    required=False,
                                                    queryset=None,
                                                    widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(TreatmentForm, self).__init__(*args, **kwargs)
        self.fields['id_doctor'].queryset = Doctor.objects.raw_as_qs("SELECT * FROM doctor;", db_user=get_group(request))
        self.fields['card_no_patient'].queryset = Patient.objects.raw_as_qs("SELECT * FROM patient;",
                                                                     db_user=get_group(request), pk='card_no')
        self.fields['treatment_drag'].queryset = Drag.objects.raw_as_qs("SELECT * FROM drag;",
                                                                     db_user=get_group(request))


class AllergyForm(forms.Form):
    allergy_prep = forms.CharField(label='Аллергия', empty_value=None, max_length=100)


class SpecialityForm(forms.Form):
    name = forms.CharField(label='Специальность', empty_value=None, max_length=45)
    department_name = forms.CharField(label='Отдел', empty_value=None, max_length=45)

    def title_field(self):
        self.cleaned_data['name'] = self.cleaned_data['name'].title()
        self.cleaned_data['department_name'] = self.cleaned_data['department_name'].title()


class DragForm(forms.Form):
    drag_name = forms.CharField(label='Лекарство', empty_value=None, max_length=100)
    id_allergy = forms.ModelChoiceField(label='Аллергия', queryset=None)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(DragForm, self).__init__(*args, **kwargs)
        self.fields['id_allergy'].queryset = Allergy.objects.raw_as_qs("SELECT * FROM allergy;",
                                                                       db_user=get_group(request))

    def title_field(self):
        self.cleaned_data['drag_name'] = self.cleaned_data['drag_name'].title()


class DoctorForm(forms.Form):
    second_name = forms.CharField(label='Фамилия', empty_value=None, max_length=45)
    first_name = forms.CharField(label='Имя', empty_value=None, max_length=45)
    third_name = forms.CharField(label='Очество', empty_value=None, max_length=45)
    ward_number = forms.IntegerField(label='Номер палаты')
    name_speciality = forms.ModelChoiceField(label='Специальность', queryset=None)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(DoctorForm, self).__init__(*args, **kwargs)
        self.fields['name_speciality'].queryset = Speciality.objects.raw_as_qs("SELECT * FROM speciality;",
                                                                       db_user=get_group(request))

    def title_field(self):
        self.cleaned_data['first_name'] = self.cleaned_data['first_name'].title()
        self.cleaned_data['second_name'] = self.cleaned_data['second_name'].title()
        self.cleaned_data['third_name'] = self.cleaned_data['third_name'].title()


class PatientForm(forms.Form):
    card_no = forms.CharField(label='Номер карты', empty_value=None, max_length=7)
    med_policy = forms.CharField(label='Номер полиса', empty_value=None, max_length=16)
    passport = forms.CharField(label='Номер паспорта', empty_value=None, max_length=10)
    second_name = forms.CharField(label='Фамилия', empty_value=None, max_length=45)
    first_name = forms.CharField(label='Имя', empty_value=None, max_length=45)
    third_name = forms.CharField(label='Очество', empty_value=None, max_length=45)
    patient_allergy = forms.ModelMultipleChoiceField(label='Аллергия',
                                                    required=False,
                                                    queryset=None,
                                                    widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(PatientForm, self).__init__(*args, **kwargs)
        self.fields['patient_allergy'].queryset = Allergy.objects.raw_as_qs("SELECT * FROM allergy;",
                                                                            db_user=get_group(request))


    def title_field(self):
        self.cleaned_data['first_name'] = self.cleaned_data['first_name'].title()
        self.cleaned_data['second_name'] = self.cleaned_data['second_name'].title()
        self.cleaned_data['third_name'] = self.cleaned_data['third_name'].title()

