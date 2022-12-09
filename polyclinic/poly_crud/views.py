from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connections
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.utils import InternalError

from poly_crud.form import TreatmentForm
from poly_crud.logic import crud_treatment, get_group, select
from poly_crud.models import Doctor, Treatment, Patient, Drag


def welcome(request):
    return render(request, 'poly_crud/welcome.html')


@login_required
def administrator(request):
    out = "Приветствую, администратор!"
    # "SELECT card_no_patient FROM treatment WHERE id = %s;"
    # "SELECT * FROM treatment_has_drag AS tg "
    # "WHERE tg.id_treatment = %s AND tg.id_drag = %s;"
    print(select(request=request, table_name='treatment', select_column=('card_no_patient', ), where_col=('id',),
                 where_val=('48',)))
    "SELECT d.id "
    "FROM drag AS d "
    "JOIN treatment_has_drag AS td ON td.id_drag = d.id "
    "WHERE td.id_treatment = %s;"
    print(select(request=request, table_name='drag', join_table=('treatment_has_drag', ), join_ids=(('id_drag', 'id'),),
                 select_column=('id', ), where_col=('id_treatment',),
                 where_val=('103',)))
    print(select(request=request, table_name='drag'))

    return HttpResponse(out)


@login_required
def patients(request):
    # patients = Patient.objects.using(get_group(request)).order_by('card_no')
    patients = select(request=request, table_name='patient', order_by='card_no')
    context = {'patients': patients}
    return render(request, 'poly_crud/patients.html', context)


@login_required
def treatments(request, card_no):
    # treatments = Treatment.objects.using(get_group(request)).filter(card_no_patient=card_no).order_by('-date_in')
    treatments = select(request=request, table_name='treatment', where_col=('card_no_patient',),
                        where_val=(card_no,), order_by='date_in', desc=True)
    context = {'treatments': treatments, 'card_no': card_no}
    return render(request, 'poly_crud/treatments.html', context)


@login_required
def edit_treatment(request, id):
    try:
        context = crud_treatment(request, id=id, group=get_group(request))
        if context.get('card_no'):
            return HttpResponseRedirect(reverse('poly_crud:card_no', args=(context.get('card_no'),)))
        return render(request, 'poly_crud/edit_treatment.html', context)
    except TypeError:
        return HttpResponse(context)


@login_required
def add_treatment(request, card_no):
    try:
        context = crud_treatment(request, card_no=card_no, group=get_group(request))
        if context.get('card_no'):
            return HttpResponseRedirect(reverse('poly_crud:card_no', args=(context.get('card_no'),)))
        return render(request, 'poly_crud/add_treatment.html', context)
    except TypeError:
        return HttpResponse(context)
