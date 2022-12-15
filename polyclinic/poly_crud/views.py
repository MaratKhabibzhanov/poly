from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from poly_crud.form import TreatmentForm, AllergyForm, SpecialityForm, DragForm, DoctorForm, PatientForm
from poly_crud.logic import *
from poly_crud.models import Doctor, Treatment, Patient, Drag, Allergy, Speciality


def welcome(request):
    return render(request, 'poly_crud/welcome.html')


@login_required
@permission_required('poly_crud.change_doctor')
def administrator(request):
    return render(request, 'poly_crud/administrator.html')


@login_required
@permission_required('poly_crud.change_allergy')
def allergies(request):
    allergies = Allergy.objects.raw_as_qs("SELECT * FROM allergy;")
    context = {'allergies': allergies}
    return render(request, 'poly_crud/allergies.html', context)


@login_required
@permission_required('poly_crud.change_allergy')
def edit_allergy(request, id):
    data = Allergy.select(request, id=id, select='select_allergy')[0]
    if request.method == 'POST':
        form = AllergyForm(request.POST)
        if request.POST.get('action') == 'Delete':
            context = Allergy.dell(request, id=id)
            if context and context.get('error'):
                return render(request, 'poly_crud/edit.html', {'form': form, 'error': context.get('error')})
            return HttpResponseRedirect(reverse('poly_crud:allergies'))
        if form.is_valid():
            context = Allergy.edit(request=request, id=id, form=form)
        if context.get('context'):
            return HttpResponseRedirect(reverse('poly_crud:allergies'))
        return render(request, 'poly_crud/edit.html', {'form': form, 'error': context.get('error')})
    else:
        form = AllergyForm(data)
    context = {'form': form}
    return render(request, 'poly_crud/edit.html', context)


@login_required
@permission_required('poly_crud.change_allergy')
def add_allergy(request):
    if request.method == 'POST':
        form = AllergyForm(request.POST)
        if form.is_valid():
            context = Allergy.add(request=request, form=form)
            if context.get('context'):
                return HttpResponseRedirect(reverse('poly_crud:allergies'))
            return render(request, 'poly_crud/add.html', {'form': form, 'error': context.get('error')})
    else:
        form = AllergyForm()
    context = {'form': form}
    return render(request, 'poly_crud/add.html', context)


@login_required
@permission_required('poly_crud.change_speciality')
def specialties(request):
    specialties = Speciality.objects.raw_as_qs("SELECT * FROM speciality;")
    context = {'specialties': specialties}
    return render(request, 'poly_crud/specialties.html', context)


@login_required
@permission_required('poly_crud.change_speciality')
def edit_speciality(request, name):
    data = Speciality.select(request, id=name, select='select_speciality')[0]
    if request.method == 'POST':
        form = SpecialityForm(request.POST)
        if request.POST.get('action') == 'Delete':
            context = Speciality.dell(request, id=name)
            if context and context.get('error'):
                return render(request, 'poly_crud/edit.html', {'form': form, 'error': context.get('error')})
            return HttpResponseRedirect(reverse('poly_crud:specialties'))
        if form.is_valid():
            form.title_field()
            context = Speciality.edit(request=request, id=name, form=form)
        if context.get('context'):
            return HttpResponseRedirect(reverse('poly_crud:specialties'))
        return render(request, 'poly_crud/edit.html', {'form': form, 'error': context.get('error')})
    else:
        form = SpecialityForm(data)
    context = {'form': form}
    return render(request, 'poly_crud/edit.html', context)


@login_required
@permission_required('poly_crud.change_speciality')
def add_speciality(request):
    if request.method == 'POST':
        form = SpecialityForm(request.POST)
        if form.is_valid():
            form.title_field()
            context = Speciality.add(request=request, form=form)
            if context.get('context'):
                return HttpResponseRedirect(reverse('poly_crud:specialties'))
            return render(request, 'poly_crud/add.html', {'form': form, 'error': context.get('error')})
    else:
        form = SpecialityForm()
    context = {'form': form}
    return render(request, 'poly_crud/add.html', context)


@login_required
@permission_required('poly_crud.change_drag')
def drags(request):
    drags = Drag.objects.raw_as_qs("SELECT * FROM drag;")
    context = {'drags': drags}
    return render(request, 'poly_crud/drags.html', context)


@login_required
@permission_required('poly_crud.change_drag')
def edit_drag(request, id):
    data = Drag.select(request, id=id, select='select_drag')[0]
    if request.method == 'POST':
        form = DragForm(request.POST, request=request)
        if request.POST.get('action') == 'Delete':
            context = Drag.dell(request, id=id)
            if context and context.get('error'):
                return render(request, 'poly_crud/edit.html', {'form': form, 'error': context.get('error')})
            return HttpResponseRedirect(reverse('poly_crud:drags'))
        if form.is_valid():
            form.title_field()
            context = Drag.edit(request=request, id=id, form=form)
        if context.get('context'):
            return HttpResponseRedirect(reverse('poly_crud:drags'))
        return render(request, 'poly_crud/edit.html', {'form': form, 'error': context.get('error')})
    else:
        form = DragForm(data, request=request)
    context = {'form': form}
    return render(request, 'poly_crud/edit.html', context)


@login_required
@permission_required('poly_crud.change_drag')
def add_drag(request):
    if request.method == 'POST':
        form = DragForm(request.POST, request=request)
        if form.is_valid():
            form.title_field()
            context = Drag.add(request=request, form=form)
            if context.get('context'):
                return HttpResponseRedirect(reverse('poly_crud:drags'))
            return render(request, 'poly_crud/add.html', {'form': form, 'error': context.get('error')})
    else:
        form = DragForm(request=request)
    context = {'form': form}
    return render(request, 'poly_crud/add.html', context)

@login_required
@permission_required('poly_crud.change_doctor')
def doctors(request):
    doctors = Doctor.objects.raw_as_qs("SELECT * FROM doctor;")
    context = {'doctors': doctors}
    return render(request, 'poly_crud/doctors.html', context)


@login_required
@permission_required('poly_crud.change_doctor')
def edit_doctor(request, id):
    data = Doctor.select(request, id=id, select='select_doctor')[0]
    if request.method == 'POST':
        form = DoctorForm(request.POST, request=request)
        if request.POST.get('action') == 'Delete':
            context = Doctor.dell(request, id=id)
            if context and context.get('error'):
                return render(request, 'poly_crud/edit.html', {'form': form, 'error': context.get('error')})
            return HttpResponseRedirect(reverse('poly_crud:doctors'))
        if form.is_valid():
            form.title_field()
            context = Doctor.edit(request=request, id=id, form=form)
        if context.get('context'):
            return HttpResponseRedirect(reverse('poly_crud:doctors'))
        return render(request, 'poly_crud/edit.html', {'form': form, 'error': context.get('error')})
    else:
        form = DoctorForm(data, request=request)
    context = {'form': form}
    return render(request, 'poly_crud/edit.html', context)


@login_required
@permission_required('poly_crud.change_doctor')
def add_doctor(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST, request=request)
        if form.is_valid():
            form.title_field()
            context = Doctor.add(request=request, form=form)
            if context.get('context'):
                return HttpResponseRedirect(reverse('poly_crud:doctors'))
            return render(request, 'poly_crud/add.html', {'form': form, 'error': context.get('error')})
    else:
        form = DoctorForm(request=request)
    context = {'form': form}
    return render(request, 'poly_crud/add.html', context)


@login_required
def treatments(request):
    # patients = Patient.objects.using(get_group(request)).order_by('card_no')
    treatments = select(request=request, table_name='patient', order_by='card_no')
    context = {'treatments': treatments}
    return render(request, 'poly_crud/treatments.html', context)


@login_required
def tr_patients(request, card_no):
    # treatments = Treatment.objects.using(get_group(request)).filter(card_no_patient=card_no).order_by('-date_in')
    treatments = select(request=request, table_name='treatment', where_col=('card_no_patient',),
                        where_val=(card_no,), order_by='date_in', desc=True)
    context = {'treatments': treatments, 'card_no': card_no}
    return render(request, 'poly_crud/tr_patients.html', context)


@login_required
def edit_treatment(request, id):
    data = Treatment.select(request, id=id, select='select_treatment')[0]
    drag = Treatment.select(request, id=id, select='select_drag', out='list')
    data['treatment_drag'] = drag
    if request.method == 'POST':
        form = TreatmentForm(request.POST, request=request)
        if request.POST.get('action') == 'Delete':
            context = Treatment.dell(request, id=id, returning='card_no_patient')
            if context and context.get('error'):
                return render(request, 'poly_crud/edit.html', {'form': form, 'error': context.get('error')})
            return HttpResponseRedirect(reverse('poly_crud:tr_patients'))
        if form.is_valid():
            context = Treatment.edit(request=request, id=id, form=form)
        if context.get('context'):
            return HttpResponseRedirect(reverse('poly_crud:tr_patients', args=(context.get('context'),)))
        return render(request, 'poly_crud/edit.html', {'form': form, 'error': context.get('error')})
    else:
        form = TreatmentForm(data, request=request)
    context = {'form': form}
    return render(request, 'poly_crud/edit.html', context)


@login_required
def add_treatment(request, card_no):
    data = {'card_no_patient': card_no}
    if request.method == 'POST':
        form = TreatmentForm(request.POST, request=request)
        if form.is_valid():
            context = Treatment.add(request=request, form=form)
            if context.get('context'):
                return HttpResponseRedirect(reverse('poly_crud:tr_patients', args=(card_no,)))
            return render(request, 'poly_crud/add.html', {'form': form, 'error': context.get('error')})
    else:
        form = TreatmentForm(data, request=request)
    context = {'form': form}
    return render(request, 'poly_crud/add.html', context)


@login_required
@permission_required('poly_crud.change_patient')
def patients(request):
    patients = Patient.objects.raw_as_qs("SELECT * FROM patient;")
    context = {'patients': patients}
    return render(request, 'poly_crud/patients.html', context)


@login_required
@permission_required('poly_crud.change_patient')
def edit_patient(request, card_no):
    data = Patient.select(request, id=card_no, select='select_patient')[0]
    drag = Patient.select(request, id=card_no, select='select_allergy', out='list')
    data['patient_allergy'] = drag
    if request.method == 'POST':
        form = PatientForm(request.POST, request=request)
        if request.POST.get('action') == 'Delete':
            context = Patient.dell(request, id=card_no)
            if context and context.get('error'):
                return render(request, 'poly_crud/edit.html', {'form': form, 'error': context.get('error')})
            return HttpResponseRedirect(reverse('poly_crud:patients'))
        if form.is_valid():
            form.title_field()
            context = Patient.edit(request=request, id=card_no, form=form)
        else:
            return render(request, 'poly_crud/edit.html', {'form': form})
        if context.get('context'):
            return HttpResponseRedirect(reverse('poly_crud:patients'))
        return render(request, 'poly_crud/edit.html', {'form': form, 'error': context.get('error')})
    else:
        form = PatientForm(data, request=request)
    context = {'form': form}
    return render(request, 'poly_crud/edit.html', context)


@login_required
@permission_required('poly_crud.change_patient')
def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST, request=request)
        if form.is_valid():
            form.title_field()
            context = Patient.add(request=request, form=form)
            if context.get('context'):
                return HttpResponseRedirect(reverse('poly_crud:patients'))
            return render(request, 'poly_crud/add.html', {'form': form, 'error': context.get('error')})
        else:
            return render(request, 'poly_crud/add.html', {'form': form})
    else:
        form = PatientForm(request=request)
    context = {'form': form}
    return render(request, 'poly_crud/add.html', context)
