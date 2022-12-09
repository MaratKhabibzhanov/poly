from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.forms import CheckboxInput, Select, RadioSelect


class UserOurRegistration(UserCreationForm):
    groups = forms.ModelChoiceField(label='Группа', queryset=Group.objects.all(), widget=RadioSelect())

    class Meta:
        model = User
        fields = ['username', 'groups', 'password1', 'password2']