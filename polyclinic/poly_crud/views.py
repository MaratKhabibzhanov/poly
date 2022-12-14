from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from poly_crud.form import TreatmentForm
from poly_crud.logic import *
from poly_crud.models import Doctor, Treatment, Patient, Drag


def welcome(request):
    return render(request, 'poly_crud/welcome.html')


@login_required
def administrator(request):
    out = "Приветствую, администратор!"
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
    data = Treatment.select(request, id=id, select='select_treatment')[0]
    drag = Treatment.select(request, id=id, select='select_drag', out='list')
    data['treatment_drag'] = drag
    if request.method == 'POST':
        if request.POST.get('action') == 'Delete':
            context = Treatment.dell(request, id=id, returning='card_no_patient')
        form = TreatmentForm(request.POST, request=request)
        if form.is_valid():
            context = Treatment.edit(request=request, id=id, form=form)
        if context.get('context'):
            return HttpResponseRedirect(reverse('poly_crud:card_no', args=(context.get('context'),)))
        return HttpResponse(context.get('error'))
    else:
        form = TreatmentForm(data, request=request)
    context = {'form': form}
    return render(request, 'poly_crud/edit_treatment.html', context)


@login_required
def add_treatment(request, card_no):
    data = {'card_no_patient': card_no}
    if request.method == 'POST':
        form = TreatmentForm(request.POST, request=request)
        if form.is_valid():
            context = Treatment.add(request=request, form=form)
            if context.get('context'):
                return HttpResponseRedirect(reverse('poly_crud:card_no', args=(card_no,)))
            return HttpResponse(context.get('error'))
    else:
        form = TreatmentForm(data, request=request)
    context = {'form': form}
    return render(request, 'poly_crud/add_treatment.html', context)
