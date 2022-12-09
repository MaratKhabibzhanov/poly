from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from users.form import UserOurRegistration


# Create your views here.
def register(request):
    if request.method != 'POST':
        form = UserOurRegistration()
    else:
        form = UserOurRegistration(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user.groups.add(request.POST.get('groups'))
            authenticated_user = authenticate(username=new_user.username, password=request.POST['password1'])
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('poly_crud:welcome'))
    context = {'form': form}
    return render(request, 'users/register.html', context)