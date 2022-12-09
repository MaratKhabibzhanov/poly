# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models, connection, connections
from django.db.models import UniqueConstraint


class MyManager(models.Manager):
    def raw_as_qs(self, raw_query, params=(), db_user='default', pk='id'):
        """Execute a raw query and return a QuerySet.  The first column in the
        result set must be the id field for the model.
        :type raw_query: str | unicode
        :type params: tuple[T] | dict[str | unicode, T]
        :rtype: django.db.models.query.QuerySet
        """
        cursor = connections[db_user].cursor()
        try:
            cursor.execute(raw_query, params)
            return self.filter(pk__in=(x[0] for x in cursor))
        finally:
            cursor.close()


class Allergy(models.Model):
    id = models.BigAutoField(primary_key=True)
    allergy_prep = models.CharField(unique=True, max_length=100)
    objects = MyManager()

    def __str__(self):
        return self.allergy_prep

    class Meta:
        managed = False
        db_table = 'allergy'


class Doctor(models.Model):
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


class Drag(models.Model):
    id = models.BigAutoField(primary_key=True)
    drag_name = models.CharField(unique=True, max_length=100)
    id_allergy = models.ForeignKey(Allergy, on_delete=models.PROTECT,
                                   db_column='id_allergy')
    objects = MyManager()

    def __str__(self):
        return self.drag_name

    class Meta:
        managed = False
        db_table = 'drag'


class Patient(models.Model):
    card_no = models.CharField(primary_key=True, max_length=7)
    med_policy = models.CharField(unique=True, max_length=16)
    passport = models.CharField(unique=True, max_length=10)
    first_name = models.CharField(max_length=45)
    second_name = models.CharField(max_length=45)
    third_name = models.CharField(max_length=45)
    id_allergy = models.ForeignKey(Allergy, on_delete=models.PROTECT,
                                   db_column='id_allergy',
                                   blank=True, null=True)
    objects = MyManager()

    def __str__(self):
        return self.card_no

    class Meta:
        managed = False
        db_table = 'patient'
        indexes = [
            models.Index(fields=['id_allergy'], name='idx_allergy'),
        ]


class Speciality(models.Model):
    name = models.CharField(primary_key=True, max_length=45)
    department_name = models.CharField(max_length=45)
    objects = MyManager()

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'speciality'


class Treatment(models.Model):
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
        #unique_together = (('id_treatment', 'id_drag'),)
        UniqueConstraint(fields=('id_treatment', 'id_drag'),
                         name='treatmenthasdrag_uq')

