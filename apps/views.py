from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, render, redirect
from django.template.defaulttags import register

from .forms import RegisterForm, PaperForm, ReviewForm
from .models import Attendee, Paper, Review

# Create your views here.

def indexPage(request):
    # This page should never be visible, replace all redirect('index')
    # calls to redirect('user_portal') defined below
    context = {}
    if request.user.is_authenticated:
        context["logged_in_user"] = request.user.attendee
    return render(request, 'apps/index.html', context)


def userPortalPage(request):
    context = {}
    return render(request, 'apps/index.html', context)


def signUpPage(request):
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
            context["signup_form"] = form
    else:
        form = RegisterForm()
        context["signup_form"] = form
    return render(request, 'apps/signup.html', context)


def signInPage(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Error: Wrong Username and/or Password!')
    return render(request, 'apps/signin.html')


def signOutPage(request):
    logout(request)
    return redirect('index')


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


def paperRetrievePage(request, pk):
    if not request.user.is_authenticated:
        return redirect('index')
    paper = get_object_or_404(Paper, pk=pk)
    form = PaperForm(data=model_to_dict(paper))
    context = { "paper_form": form }
    return render(request, 'apps/paper.html', context)


def paperUpdatePage(request, pk):
    if not request.user.is_authenticated:
        return redirect('index')
    context = {}
    paper = get_object_or_404(Paper, pk=pk)
    if request.POST:
        form = PaperForm(request.POST, instance=paper)
        if form.is_valid():
            form.save()
        return redirect('index')
    else:
        form = PaperForm(data=model_to_dict(paper))
        context["paper_form"] = form
    return render(request, 'apps/paper_update.html', context)


def paperDeletePage(request, pk):
    context = {}
    paper = get_object_or_404(Paper, pk=pk)
    if request.POST:
        paper.delete()
        return redirect('index')
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


def reviewCreatePage(request):
    if not request.user.is_authenticated:
        return redirect('index')
    reviewer = request.user.attendee
    if not reviewer.is_reviewer:
        raise PermissionDenied
    if request.POST:
        form = ReviewForm(request.POST)
        form.reviewer = reviewer
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = reviewer
            review.save()
        return redirect('index')
    else:
        form = ReviewForm()
        context = {
            "review_form": form,
            "reviewer": str(reviewer)
        }
        return render(request, "apps/review_create.html", context)


def reviewRetrievePage(request, pk):
    if not request.user.is_authenticated:
        return redirect('index')
    reviewer = request.user.attendee
    if not reviewer.is_reviewer:
        raise PermissionDenied
    review = get_object_or_404(Review, pk=pk)
    form = ReviewForm(data=model_to_dict(review))
    context = { 
        "review_form": form,
        "reviewer": str(reviewer)
    }
    return render(request, 'apps/review.html', context)


def reviewUpdatePage(request, pk):
    if not request.user.is_authenticated:
        return redirect('index')
    reviewer = request.user.attendee
    if not reviewer.is_reviewer:
        raise PermissionDenied
    context = {}
    review = get_object_or_404(Review, pk=pk)
    if request.POST:
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
        return redirect('index')
    else:
        form = ReviewForm(data=model_to_dict(review))
        context["review_form"] = form
    return render(request, 'apps/review_update.html', context)
    
