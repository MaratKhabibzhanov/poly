from django import forms
from django.contrib.auth.models import User
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

