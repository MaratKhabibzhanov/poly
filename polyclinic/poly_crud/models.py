# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth import get_user
from django.db import models, connections
from django.db.models import UniqueConstraint
from django.db.utils import InternalError, IntegrityError
from psycopg2.sql import SQL, Literal, Identifier


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def get_group(request):
    user = get_user(request)
    group = 'doctor' if user.groups.filter(name='Доктор').exists() else 'default'
    return group


class MyManager(models.Manager):
    def raw_as_qs(self, raw_query, params=(), db_user='default'):
        cursor = connections[db_user].cursor()
        try:
            cursor.execute(raw_query, params)
            return self.filter(pk__in=(x[0] for x in cursor))
        finally:
            cursor.close()


class Crud():
    @classmethod
    def data_preparation(cls, form):
        name = cls.__name__
        clean_data = form.cleaned_data
        if name == 'Treatment':
            form_data = (clean_data.get('date_in'), clean_data.get('date_out'), clean_data.get('diagnosis'),
                         clean_data.get('symptom'), clean_data.get('id_doctor').id,
                         clean_data.get('card_no_patient').card_no)
            form_drag = [drag.id for drag in clean_data.get('treatment_drag')]
            return form_data, form_drag
        elif name == 'Doctor':
            form_data = (clean_data.get('first_name'), clean_data.get('second_name'), clean_data.get('third_name'),
                         clean_data.get('ward_number'), clean_data.get('name_speciality').name)
            return form_data, None
        elif name == 'Drag':
            form_data = (clean_data.get('drag_name'), clean_data.get('id_allergy').id)
            return form_data, None
        form_data = tuple([clean_data.get(field) for field in cls.fields])
        form_allergy = [allergy.id for allergy in clean_data.get('patient_allergy')] if name == 'Patient' else None
        return form_data, form_allergy

    @classmethod
    def select(cls, request, id, select, out='dict'):
        stmt = cls.select_queryes.get(select)
        with connections[get_group(request)].cursor() as cursor:
            if out == 'dict':
                cursor.execute(stmt, [id, ])
                return dictfetchall(cursor)
            elif out == 'list':
                cursor.execute(stmt, [id, ])
                return [row[0] for row in cursor.fetchall()]

    @classmethod
    def add(cls, request, form):
        form_data, form_slave = cls.data_preparation(form)
        with connections[get_group(request)].cursor() as cursor:
            try:
                cursor.execute(cls.insert_master, [form_data, ])
                if form_slave:
                    id = cursor.fetchone()[0]
                    for slave_id in form_slave:
                        cursor.execute(cls.insert_slave, [(id, slave_id), ])
                context = {'context': form_data[-1]}
                return context
            except InternalError as err:
                stmt = SQL(cls.del_master).format(id=Literal(id), ret=Identifier('id'))
                cursor.execute(stmt)
                error = str(err).split('\n')[0]
                return {'error': error}
            except IntegrityError:
                return {'error': 'Такая запись уже есть!'}

    @classmethod
    def edit(cls, request, id, form):
        form_data, form_slave = cls.data_preparation(form)
        with connections[get_group(request)].cursor() as cursor:
            try:
                cursor.execute(cls.update_master, [form_data, id])
                if form_slave:
                    cursor.execute(cls.select_slave, [id, ])
                    table_slave = [slave[cls.slave_id] for slave in dictfetchall(cursor)]
                    for drag in form_slave:
                        if drag not in table_slave:
                            cursor.execute(cls.insert_slave, [(id, drag), ])
                        else:
                            table_slave.remove(drag)
                    for drag in table_slave:
                        cursor.execute(cls.del_slave, [id, drag])
                context = {'context': form_data[-1]}
                return context
            except InternalError as err:
                error = str(err).split('\n')[0]
                return {'error': error}
            except IntegrityError:
                return {'error': 'Такая запись уже есть!'}

    @classmethod
    def dell(cls, request, id, returning=None):
        stmt = SQL(cls.del_master).format(id=Literal(id),
                                          ret=Identifier(returning) if returning else None)
        with connections[get_group(request)].cursor() as cursor:
            try:
                cursor.execute(stmt)
                if returning:
                    context = {'context': cursor.fetchone()[0]}
                    return context
            except InternalError as err:
                error = str(err).split('\n')[0]
                return {'error': error}
            except IntegrityError:
                return {'error': 'Эту запись нельзя удалить! Есть связанные с ней данные!'}


class Allergy(Crud, models.Model):
    id = models.BigAutoField(primary_key=True)
    allergy_prep = models.CharField(unique=True, max_length=100)
    objects = MyManager()

    fields = ('allergy_prep',)
    select_allergy = "SELECT * FROM allergy WHERE id = %s;"
    select_queryes = {'select_allergy': select_allergy}

    del_master = "DELETE FROM allergy WHERE id = {id}"

    insert_master = """INSERT INTO allergy (allergy_prep) VALUES %s RETURNING id;"""

    update_master = """UPDATE allergy SET allergy_prep = %s WHERE id = %s;"""

    def __str__(self):
        return self.allergy_prep

    class Meta:
        managed = False
        db_table = 'allergy'


class Doctor(Crud, models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=45)
    second_name = models.CharField(max_length=45)
    third_name = models.CharField(max_length=45)
    ward_number = models.SmallIntegerField(unique=True)
    name_speciality = models.ForeignKey('Speciality',
                                        on_delete=models.PROTECT,
                                        db_column='name_speciality',
                                        blank=True, null=True)
    objects = MyManager()

    select_doctor = "SELECT * FROM doctor WHERE id = %s;"
    select_queryes = {'select_doctor': select_doctor}

    del_master = "DELETE FROM doctor WHERE id = {id};"

    insert_master = """INSERT INTO doctor (first_name, second_name, third_name, ward_number, name_speciality) 
    VALUES %s RETURNING id;"""

    update_master = """UPDATE doctor SET (first_name, second_name, third_name, ward_number, name_speciality)  = %s 
    WHERE id = %s;"""

    def __str__(self):
        return f'{self.id} {self.name_speciality} {self.first_name} {self.second_name} {self.third_name}'

    class Meta:
        managed = False
        db_table = 'doctor'
        indexes = [
            models.Index(fields=['first_name'], name='idx_first_name'),
            models.Index(fields=['second_name'], name='idx_second_name'),
            models.Index(fields=['third_name'], name='idx_third_name'),
            models.Index(fields=['name_speciality'], name='idx_name_speciality'),
        ]


class Drag(Crud, models.Model):
    id = models.BigAutoField(primary_key=True)
    drag_name = models.CharField(unique=True, max_length=100)
    id_allergy = models.ForeignKey(Allergy, on_delete=models.PROTECT,
                                   db_column='id_allergy')
    objects = MyManager()

    select_drag = "SELECT * FROM drag WHERE id = %s;"
    select_queryes = {'select_drag': select_drag}

    del_master = "DELETE FROM drag WHERE id = {id};"

    insert_master = """INSERT INTO drag (drag_name, id_allergy) VALUES %s RETURNING id;"""

    update_master = """UPDATE drag SET (drag_name, id_allergy) = %s WHERE id = %s;"""

    def __str__(self):
        return self.drag_name

    class Meta:
        managed = False
        db_table = 'drag'


class Patient(Crud, models.Model):
    card_no = models.CharField(primary_key=True, max_length=7)
    med_policy = models.CharField(unique=True, max_length=16)
    passport = models.CharField(unique=True, max_length=10)
    first_name = models.CharField(max_length=45)
    second_name = models.CharField(max_length=45)
    third_name = models.CharField(max_length=45)
    objects = MyManager()

    slave_id = 'id_allergy'
    fields = ('card_no', 'med_policy', 'passport', 'first_name', 'second_name', 'third_name')
    select_patient = "SELECT * FROM patient WHERE card_no = %s;"
    select_allergy = """SELECT a.id FROM allergy AS a 
                    JOIN patient_has_allergy AS pa ON pa.id_allergy = a.id WHERE pa.card_no_patient = %s;"""
    select_slave = "SELECT id_allergy FROM patient_has_allergy WHERE card_no_patient = %s;"
    select_queryes = {'select_patient': select_patient, 'select_allergy': select_allergy}

    del_master = "DELETE FROM patient WHERE card_no = {id};"
    del_slave = "DELETE FROM patient_has_allergy WHERE card_no_patient = %s AND id_allergy = %s;"

    insert_master = """INSERT INTO patient 
               (card_no, med_policy, passport, first_name, second_name, third_name) VALUES %s RETURNING card_no;"""
    insert_slave = "INSERT INTO patient_has_allergy VALUES %s;"

    update_master = """UPDATE patient SET (card_no, med_policy, passport, first_name, second_name, third_name) = %s 
        WHERE card_no = %s;"""


    def __str__(self):
        return self.card_no

    class Meta:
        managed = False
        db_table = 'patient'


class Speciality(Crud, models.Model):
    name = models.CharField(primary_key=True, max_length=45)
    department_name = models.CharField(max_length=45)
    objects = MyManager()

    fields = ('name', 'department_name')
    select_speciality = "SELECT * FROM speciality WHERE name = %s;"
    select_queryes = {'select_speciality': select_speciality}

    del_master = "DELETE FROM speciality WHERE name = {id}"

    insert_master = """INSERT INTO speciality (name, department_name) VALUES %s RETURNING name;"""

    update_master = """UPDATE speciality SET (name, department_name) = %s WHERE name = %s;"""

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'speciality'


class Treatment(Crud, models.Model):
    id = models.BigAutoField(primary_key=True)
    date_in = models.DateField()
    date_out = models.DateField(blank=True, null=True)
    diagnosis = models.CharField(max_length=120, blank=True, null=True)
    symptom = models.CharField(max_length=120)
    id_doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT,
                                  db_column='id_doctor')
    card_no_patient = models.ForeignKey(Patient, on_delete=models.CASCADE,
                                        db_column='card_no_patient')
    objects = MyManager()

    slave_id = 'id_drag'
    select_treatment = "SELECT * FROM treatment WHERE id = %s;"
    select_drag = """SELECT d.id FROM drag AS d 
                JOIN treatment_has_drag AS td ON td.id_drag = d.id WHERE td.id_treatment = %s;"""
    select_slave = "SELECT id_drag FROM treatment_has_drag WHERE id_treatment = %s;"
    select_queryes = {'select_treatment': select_treatment, 'select_drag': select_drag}

    del_master = "DELETE FROM treatment WHERE id = {id} RETURNING {ret};"
    del_slave = "DELETE FROM treatment_has_drag WHERE id_treatment = %s AND id_drag = %s;"

    insert_master = """INSERT INTO treatment 
           (date_in, date_out, diagnosis, symptom, id_doctor, card_no_patient) 
           VALUES %s RETURNING id;"""
    insert_slave = "INSERT INTO treatment_has_drag VALUES %s;"

    update_master = """UPDATE treatment SET (date_in, date_out, diagnosis, symptom, id_doctor, card_no_patient) = %s 
    WHERE id = %s;"""

    class Meta:
        managed = False
        db_table = 'treatment'
        #unique_together = (('id_doctor', 'card_no_patient', 'date_in'),)
        UniqueConstraint(fields=('id_doctor', 'card_no_patient', 'date_in'),
                         name='treatment_uq')
        indexes = [
            models.Index(fields=['symptom'], name='idx_symptom'),
            models.Index(fields=['card_no_patient'], name='idx_card_no'),
            models.Index(fields=['id_doctor'], name='idx_doctor'),
        ]


class TreatmentHasDrag(models.Model):
    id_treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE,
                                     db_column='id_treatment', primary_key=True)
    id_drag = models.ForeignKey(Drag, on_delete=models.PROTECT,
                                db_column='id_drag')
    objects = MyManager()

    class Meta:
        managed = False
        db_table = 'treatment_has_drag'
        # unique_together = (('id_treatment', 'id_drag'),)
        UniqueConstraint(fields=('id_treatment', 'id_drag'),
                         name='treatmenthasdrag_uq')


class PatientHasAllergy(models.Model):
    card_no_patient = models.ForeignKey(Patient, on_delete=models.CASCADE,
                                        db_column='card_no_patient', primary_key=True)
    id_allergy = models.ForeignKey(Allergy, on_delete=models.PROTECT,
                                   db_column='id_allergy')
    objects = MyManager()

    class Meta:
        managed = False
        db_table = 'patient_has_allergy'
        # unique_together = (('card_no_patient', 'id_allergy'),)
        UniqueConstraint(fields=('card_no_patient', 'id_allergy'),
                         name='patienthasallergy_uq')

