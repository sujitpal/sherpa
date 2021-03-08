from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.template.defaulttags import register

from .forms import RegisterForm, PaperForm
from .models import Attendee, Paper

# Create your views here.

def indexPage(request):
    # This page should never be visible, replace all redirect('index')
    # calls to redirect('user_portal') defined below
    return render(request, 'apps/index.html', {})


def userPortalPage(request):
    context = {}
    return render(request, 'apps/index.html', context)


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


def paperCreatePage(request):
    if not request.user.is_authenticated:
        return redirect('index')
    context = {}
    if request.POST:
        form = PaperForm(request.POST)
        form.primary_author = request.user.attendee
        if form.is_valid():
            form.save()
        return redirect('index')
    else:
        form = PaperForm()
        context["paper_form"] = form
        return render(request, "apps/paper_create.html", context)


def paperRetrievePage(request):
    context = {}
    return render(request, 'apps/paper.html', context)

def paperUpdatePage(request):
    context = {}
    return render(request, 'apps/paper_update.html', context)

def paperDeletePage(request):
    context = {}
    return render(request, 'apps/paper_delete.html', context)

def paperListPage(request):
    paper_list = Paper.objects.all()
    num_papers = paper_list.count()
    page = request.GET.get('page', 1)
    paginator = Paginator(paper_list, 10)
    try:
        papers = paginator.page(page)
    except PageNotAnInteger:
        papers = paginator.page(1)
    except EmptyPage:
        papers = paginator.page(paginator.num_pages)
    context = { 
        "papers" : papers,
        "num_papers": num_papers
    }
    return render(request, 'apps/papers.html', context)




