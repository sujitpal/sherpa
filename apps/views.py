from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

from .forms import RegisterForm

# Create your views here.

def indexPage(request):
    return render(request, 'apps/index.html', {})


def registerPage(request):
    context = {}
    if request.POST:
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.attendee.name = form.cleaned_data.get('name')
            user.attendee.email = form.cleaned_data.get('email')
            user.attendee.org = form.cleaned_data.get('org')
            user.attendee.timezone = form.cleaned_data.get('timezone')
            user.username = user.attendee.email
            user.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
        else:
            context["register_form"] = form
    else:
        form = RegisterForm()
        context["register_form"] = form
    return render(request, 'apps/register.html', context)
