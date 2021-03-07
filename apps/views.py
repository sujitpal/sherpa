from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.template.defaulttags import register

from .forms import RegisterForm
from .models import Attendee

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


def attendeeListPage(request):
    attendee_list = Attendee.objects.exclude(name__exact='').order_by('user__id')
    num_attendees = attendee_list.count()
    page = request.GET.get('page', 1)
    paginator = Paginator(attendee_list, 10)
    try:
        attendees = paginator.page(page)
    except PageNotAnInteger:
        attendees = paginator.page(1)
    except EmptyPage:
        attendees = paginator.page(paginator.num_pages)
    context = { 
        "attendees" : attendees,
        "num_attendees": num_attendees
    }
    return render(request, "apps/attendees.html", context)
