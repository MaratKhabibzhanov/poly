from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from poly_crud.form import TreatmentForm, AllergyForm, SpecialityForm, DragForm, DoctorForm, PatientForm, QueryaForm, \
    QuerybForm, QuerycForm
from poly_crud.models import Doctor, Treatment, Patient, Drag, Allergy, Speciality, get_group, query_a, query_b, query_c


def welcome(request):
    return render(request, 'poly_crud/welcome.html')


@login_required
@permission_required('poly_crud.change_doctor')
def administrator(request):
    return render(request, 'poly_crud/administrator.html')


@login_required
@permission_required('poly_crud.change_allergy')
def allergies(request):
    allergies = Allergy.objects.raw_as_qs("SELECT * FROM allergy;", db_user=get_group(request)).order_by('allergy_prep')
    context = {'allergies': allergies}
    return render(request, 'poly_crud/allergies.html', context)


@login_required
@permission_required('poly_crud.change_allergy')
def edit_allergy(request, id):
    data = Allergy.select(request, id=id, select='select_allergy')[0]
    if request.method == 'POST':
        form = AllergyForm(request.POST)
        if request.POST.get('action') == 'Delete':
            query = Allergy.dell(request, id=id)
            if query and query.get('error'):
                context = {'form': form, 'error': query.get('error'), 'title': 'Редактировать аллергию'}
                return render(request, 'poly_crud/edit.html', context)
            return HttpResponseRedirect(reverse('poly_crud:allergies'))
        if form.is_valid():
            form.title_field()
            query = Allergy.edit(request=request, id=id, form=form)
        if query.get('context'):
            return HttpResponseRedirect(reverse('poly_crud:allergies'))
        context = {'form': form, 'error': query.get('error'), 'title': 'Редактировать аллергию'}
        return render(request, 'poly_crud/edit.html', context)
    else:
        form = AllergyForm(data)
    context = {'form': form, 'title': 'Редактировать аллергию'}
    return render(request, 'poly_crud/edit.html', context)


@login_required
@permission_required('poly_crud.change_allergy')
def add_allergy(request):
    if request.method == 'POST':
        form = AllergyForm(request.POST)
        if form.is_valid():
            form.title_field()
            query = Allergy.add(request=request, form=form)
            if query.get('context'):
                return HttpResponseRedirect(reverse('poly_crud:allergies'))
            context = {'form': form, 'error': query.get('error'), 'title': 'Добавить аллергию'}
            return render(request, 'poly_crud/add.html', context)
    else:
        form = AllergyForm()
    context = {'form': form, 'title': 'Добавить аллергию'}
    return render(request, 'poly_crud/add.html', context)


@login_required
@permission_required('poly_crud.change_speciality')
def specialties(request):
    specialties = Speciality.objects.raw_as_qs("SELECT * FROM speciality;", db_user=get_group(request)).order_by('name')
    context = {'specialties': specialties}
    return render(request, 'poly_crud/specialties.html', context)


@login_required
@permission_required('poly_crud.change_speciality')
def edit_speciality(request, name):
    data = Speciality.select(request, id=name, select='select_speciality')[0]
    if request.method == 'POST':
        form = SpecialityForm(request.POST)
        if request.POST.get('action') == 'Delete':
            query = Speciality.dell(request, id=name)
            if query and query.get('error'):
                context = {'form': form, 'error': query.get('error'), 'title': 'Редактировать специальность'}
                return render(request, 'poly_crud/edit.html', context)
            return HttpResponseRedirect(reverse('poly_crud:specialties'))
        if form.is_valid():
            form.title_field()
            query = Speciality.edit(request=request, id=name, form=form)
        if query.get('context'):
            return HttpResponseRedirect(reverse('poly_crud:specialties'))
        context = {'form': form, 'error': query.get('error'), 'title': 'Редактировать специальность'}
        return render(request, 'poly_crud/edit.html', context)
    else:
        form = SpecialityForm(data)
    context = {'form': form, 'title': 'Редактировать специальность'}
    return render(request, 'poly_crud/edit.html', context)


@login_required
@permission_required('poly_crud.change_speciality')
def add_speciality(request):
    if request.method == 'POST':
        form = SpecialityForm(request.POST)
        if form.is_valid():
            form.title_field()
            query = Speciality.add(request=request, form=form)
            if query.get('context'):
                return HttpResponseRedirect(reverse('poly_crud:specialties'))
            context = {'form': form, 'error': query.get('error'), 'title': 'Добавить специальность'}
            return render(request, 'poly_crud/add.html', context)
    else:
        form = SpecialityForm()
    context = {'form': form, 'title': 'Добавить специальность'}
    return render(request, 'poly_crud/add.html', context)


@login_required
@permission_required('poly_crud.change_drag')
def drags(request):
    drags = Drag.objects.raw_as_qs("SELECT * FROM drag;", db_user=get_group(request)).order_by('drag_name')
    context = {'drags': drags}
    return render(request, 'poly_crud/drags.html', context)


@login_required
@permission_required('poly_crud.change_drag')
def edit_drag(request, id):
    data = Drag.select(request, id=id, select='select_drag')[0]
    if request.method == 'POST':
        form = DragForm(request.POST, request=request)
        if request.POST.get('action') == 'Delete':
            query = Drag.dell(request, id=id)
            if query and query.get('error'):
                context = {'form': form, 'error': query.get('error'), 'title': 'Редактировать лекарство'}
                return render(request, 'poly_crud/edit.html', context)
            return HttpResponseRedirect(reverse('poly_crud:drags'))
        if form.is_valid():
            form.title_field()
            query = Drag.edit(request=request, id=id, form=form)
        if query.get('context'):
            return HttpResponseRedirect(reverse('poly_crud:drags'))
        context = {'form': form, 'error': query.get('error'), 'title': 'Редактировать лекарство'}
        return render(request, 'poly_crud/edit.html', context)
    else:
        form = DragForm(data, request=request)
    context = {'form': form, 'title': 'Редактировать лекарство'}
    return render(request, 'poly_crud/edit.html', context)


@login_required
@permission_required('poly_crud.change_drag')
def add_drag(request):
    if request.method == 'POST':
        form = DragForm(request.POST, request=request)
        if form.is_valid():
            form.title_field()
            query = Drag.add(request=request, form=form)
            if query.get('context'):
                return HttpResponseRedirect(reverse('poly_crud:drags'))
            context = {'form': form, 'error': query.get('error'), 'title': 'Добавить лекарство'}
            return render(request, 'poly_crud/add.html', context)
    else:
        form = DragForm(request=request)
    context = {'form': form, 'title': 'Добавить лекарство'}
    return render(request, 'poly_crud/add.html', context)

@login_required
@permission_required('poly_crud.change_doctor')
def doctors(request):
    doctors = Doctor.objects.raw_as_qs("SELECT * FROM doctor;", db_user=get_group(request)).order_by('second_name')
    context = {'doctors': doctors}
    return render(request, 'poly_crud/doctors.html', context)


@login_required
@permission_required('poly_crud.change_doctor')
def edit_doctor(request, id):
    data = Doctor.select(request, id=id, select='select_doctor')[0]
    if request.method == 'POST':
        form = DoctorForm(request.POST, request=request)
        if request.POST.get('action') == 'Delete':
            query = Doctor.dell(request, id=id)
            if query and query.get('error'):
                context = {'form': form, 'error': query.get('error'), 'title': 'Редактировать доктора'}
                return render(request, 'poly_crud/edit.html', context)
            return HttpResponseRedirect(reverse('poly_crud:doctors'))
        if form.is_valid():
            form.title_field()
            query = Doctor.edit(request=request, id=id, form=form)
        if query.get('context'):
            return HttpResponseRedirect(reverse('poly_crud:doctors'))
        context = {'form': form, 'error': query.get('error'), 'title': 'Редактировать доктора'}
        return render(request, 'poly_crud/edit.html', context)
    else:
        form = DoctorForm(data, request=request)
    context = {'form': form, 'title': 'Редактировать доктора'}
    return render(request, 'poly_crud/edit.html', context)


@login_required
@permission_required('poly_crud.change_doctor')
def add_doctor(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST, request=request)
        if form.is_valid():
            form.title_field()
            query = Doctor.add(request=request, form=form)
            if query.get('context'):
                return HttpResponseRedirect(reverse('poly_crud:doctors'))
            context = {'form': form, 'error': query.get('error'), 'title': 'Добавить доктора'}
            return render(request, 'poly_crud/add.html', context)
    else:
        form = DoctorForm(request=request)
    context = {'form': form, 'title': 'Добавить доктора'}
    return render(request, 'poly_crud/add.html', context)


@login_required
def treatments(request):
    patients = Patient.objects.raw_as_qs("SELECT * FROM patient;",
                                         db_user=get_group(request)).order_by('card_no')
    context = {'patients': patients}
    return render(request, 'poly_crud/treatments.html', context)


@login_required
def tr_patients(request, card_no):
    treatments = Treatment.objects.raw_as_qs("SELECT * FROM treatment WHERE card_no_patient = %s ",
                                             params=(card_no,),
                                             db_user=get_group(request)).order_by('-date_in')
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
            query = Treatment.dell(request, id=id, returning='card_no_patient')
            if query and query.get('error'):
                context = {'form': form, 'error': query.get('error'), 'title': 'Редактировать лечение'}
                return render(request, 'poly_crud/edit.html', context)
            return HttpResponseRedirect(reverse('poly_crud:tr_patients', args=(query.get('context'),)))
        if form.is_valid():
            query = Treatment.edit(request=request, id=id, form=form)
        if query.get('context'):
            return HttpResponseRedirect(reverse('poly_crud:tr_patients', args=(query.get('context'),)))
        context = {'form': form, 'error': query.get('error'), 'title': 'Редактировать лечение'}
        return render(request, 'poly_crud/edit.html', context)
    else:
        form = TreatmentForm(data, request=request)
    context = {'form': form, 'title': 'Редактировать лечение'}
    return render(request, 'poly_crud/edit.html', context)


@login_required
def add_treatment(request, card_no):
    data = {'card_no_patient': card_no}
    if request.method == 'POST':
        form = TreatmentForm(request.POST, request=request)
        if form.is_valid():
            query = Treatment.add(request=request, form=form)
            if query.get('context'):
                return HttpResponseRedirect(reverse('poly_crud:tr_patients', args=(card_no,)))
            context = {'form': form, 'error': query.get('error'), 'title': 'Добавить лечение'}
            return render(request, 'poly_crud/add.html', context)
    else:
        form = TreatmentForm(data, request=request)
    context = {'form': form, 'title': 'Добавить лечение'}
    return render(request, 'poly_crud/add.html', context)


@login_required
@permission_required('poly_crud.change_patient')
def patients(request):
    patients = Patient.objects.raw_as_qs("SELECT * FROM patient;", db_user=get_group(request)).order_by('second_name')
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
            query = Patient.dell(request, id=card_no)
            if query and query.get('error'):
                context = {'form': form, 'error': query.get('error'), 'title': 'Редактировать пациента'}
                return render(request, 'poly_crud/edit.html', context)
            return HttpResponseRedirect(reverse('poly_crud:patients'))
        if form.is_valid():
            form.title_field()
            query = Patient.edit(request=request, id=card_no, form=form)
        else:
            context = {'form': form, 'title': 'Редактировать пациента'}
            return render(request, 'poly_crud/edit.html', context)
        if query.get('context'):
            return HttpResponseRedirect(reverse('poly_crud:patients'))
        context = {'form': form, 'error': query.get('error'), 'title': 'Редактировать пациента'}
        return render(request, 'poly_crud/edit.html', context)
    else:
        form = PatientForm(data, request=request)
    context = {'form': form, 'title': 'Редактировать пациента'}
    return render(request, 'poly_crud/edit.html', context)


@login_required
@permission_required('poly_crud.change_patient')
def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST, request=request)
        if form.is_valid():
            form.title_field()
            query = Patient.add(request=request, form=form)
            if query.get('context'):
                return HttpResponseRedirect(reverse('poly_crud:patients'))
            context = {'form': form, 'error': query.get('error'), 'title': 'Добавить пациента'}
            return render(request, 'poly_crud/add.html', context)
        else:
            context = {'form': form, 'title': 'Добавить пациента'}
            return render(request, 'poly_crud/add.html', context)
    else:
        form = PatientForm(request=request)
    context = {'form': form, 'title': 'Добавить пациента'}
    return render(request, 'poly_crud/add.html', context)

@login_required
@permission_required('poly_crud.change_patient')
def queries(request):
    error = ''
    if request.method == 'POST':
        form_a = QueryaForm(request.POST)
        form_b = QuerybForm(request.POST)
        form_c = QuerycForm(request.POST)
        if form_a.is_valid():
            clean_data = form_a.cleaned_data
            query = query_a(request, clean_data.get('symptom'))
            return render(request, 'poly_crud/query_a.html', {'query': query})
        elif form_b.is_valid():
            clean_data = form_b.cleaned_data
            query = query_b(request, clean_data.get('name_speciality'))
            return render(request, 'poly_crud/query_b.html', {'query': query})
        elif form_c.is_valid():
            clean_data = form_c.cleaned_data
            query = query_c(request, clean_data.get('days'))
            return render(request, 'poly_crud/query_c.html', {'query': query})
        else:
            error = 'Форма заполненна некорректно'
    form_a = QueryaForm()
    form_b = QuerybForm()
    form_c = QuerycForm()
    context = {
        'form_a': form_a,
        'form_b': form_b,
        'form_c': form_c,
        'error': error,
    }
    return render(request, 'poly_crud/queries.html', context)
