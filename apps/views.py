from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, render, redirect
from django.template.defaulttags import register

from .forms import (
    RegisterForm, 
    ProfileForm,
    SpeakerForm,
    PaperForm, 
    ReviewForm
)
from .models import Attendee, Paper, Review

# Create your views here.

def indexPage(request):
    # This page should never be visible, replace all redirect('index')
    # calls to redirect('user_portal') defined below
    context = {}
    if request.user.is_authenticated:
        context["logged_in_user"] = request.user.attendee
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
            username = form.cleaned_data.get('email')
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
        "num_attendees": num_attendees,
        "logged_in_user": request.user.attendee
    }
    return render(request, "apps/attendees.html", context)


def attendeeProfilePage(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.POST:
        form = ProfileForm(request.POST, instance=request.user.attendee)
        if form.is_valid():
            form.save()
        return redirect('index')
    else:
        initial_data = {
            'name': request.user.attendee.name,
            'email': request.user.attendee.email,
            'org': request.user.attendee.org,
            'timezone': request.user.attendee.timezone
        }
        form = ProfileForm(initial=initial_data)
        context = {
            "profile_form": form,
            "logged_in_user": request.user.attendee
        }
        return render(request, 'apps/attendee_profile_update.html', context)


def _is_speaker(attendee):
    # check if attendee has any papers that are accepted
    num_papers_accepted = Paper.objects.filter(
        primary_author__exact=attendee,
        is_accepted=True).count()
    return num_papers_accepted > 0


def attendeeSpeakerUpdatePage(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if not _is_speaker(request.user.attendee):
        return redirect('index')
    if request.POST:
        form = SpeakerForm(request.POST, instance=request.user.attendee)
        speaker_bio = form.cleaned_data.get("speaker_bio")
        print("speaker bio:", speaker_bio)
        if form.is_valid():
            form.save()
        return redirect('index')
    else:
        initial_data = {
            'speaker_bio': request.user.attendee.speaker_bio,
            'speaker_avatar': request.user.attendee.speaker_avatar
        }
        form = SpeakerForm(initial=initial_data)
        context = {
            "speaker_form": form,
            "logged_in_user": request.user.attendee
        }
        return render(request, 'apps/attendee_speakerbio_update.html', context)


def attendeeSpeakerViewPage(request, pk):
    logged_in_user = None
    if request.user.is_authenticated:
        logged_in_user = request.user.attendee
    speaker = get_object_or_404(Attendee, pk=pk)
    if not _is_speaker(speaker):
        return redirect('index')
    context = {
        "speaker": speaker,
        "logged_in_user": logged_in_user
    }
    return render(request, "apps/attendee_speakerbio_view.html", context)


def paperCreatePage(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.POST:
        form = PaperForm(request.POST)
        form.primary_author = request.user.attendee
        if form.is_valid():
            form.save()
        return redirect('index')
    else:
        form = PaperForm()
        context = {
            'paper_form': form,
            'logged_in_user': request.user.attendee
        }
        return render(request, "apps/paper_create.html", context)


def paperRetrievePage(request, pk):
    paper = get_object_or_404(Paper, pk=pk)
    # TODO: paper is visible to general public only if accepted, otherwise
    # to organizer and author / co-authors of paper
    if not paper.is_accepted:
        return redirect('index')
    paper_coauthors = ", ".join([ca.name for ca in paper.co_authors.all()])
    context = {
        "paper": paper,
        "paper_author": paper.primary_author.name,
        "paper_coauthors": paper_coauthors,
        "logged_in_user": request.user.attendee
    }
    return render(request, 'apps/paper.html', context)


def paperUpdatePage(request, pk):
    if not request.user.is_authenticated:
        return redirect('index')
    paper = get_object_or_404(Paper, pk=pk)
    if request.POST:
        form = PaperForm(request.POST, instance=paper)
        if form.is_valid():
            form.save()
        return redirect('index')
    else:
        form = PaperForm(data=model_to_dict(paper))
        context = {
            "paper_id": paper.id,
            "paper_form": form
        }
        return render(request, 'apps/paper_update.html', context)


def paperDeletePage(request, pk):
    context = {}
    paper = get_object_or_404(Paper, pk=pk)
    if request.POST:
        paper.delete()
        return redirect('index')
    return render(request, 'apps/paper_delete.html', context)


def paperListPage(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if not request.user.attendee.is_organizer:
        return redirect('index')
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
        "num_papers": num_papers,
        "logged_in_user": request.user.attendee
    }
    return render(request, 'apps/papers.html', context)


def reviewCreatePage(request, pk):
    if not request.user.is_authenticated:
        return redirect('index')
    if not request.user.attendee.is_reviewer:
        return redirect('index')
    paper = get_object_or_404(Paper, pk=pk)
    if request.POST:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review_form = form.save(commit=False)
            review_form.reviewer = request.user.attendee
            review_form.paper = paper
            review_form.save()
        return redirect('index')
    else:
        init_data = {
            "reviewer": request.user.attendee,
            "paper": paper
        }
        form = ReviewForm(initial=init_data)
        context = {
            "review_form": form,
            "init_data": init_data,
            "logged_in_user": request.user.attendee
        }
        return render(request, "apps/review_create.html", context)


def _get_star_rating(review_score):
    if review_score == "Strong Accept":
        star_rating = 4
    elif review_score == "Accept":
        star_rating = 3
    elif review_score == "Maybe Accept":
        star_rating = 2
    elif review_score == "Reject":
        star_rating = 1
    else:
        star_rating = 0
    return star_rating


def reviewRetrievePage(request, pk):
    if not request.user.is_authenticated:
        return redirect('index')
    if not request.user.attendee.is_reviewer:
        return redirect('index')
    paper = get_object_or_404(Paper, pk=pk)
    review = Review.objects.get(paper=paper, reviewer=request.user.attendee)
    star_rating = range(_get_star_rating(review.score))
    context = { 
        "review": review,
        "logged_in_user": request.user.attendee,
        "star_rating": star_rating
    }
    return render(request, 'apps/review.html', context)


def reviewUpdatePage(request, pk):
    if not request.user.is_authenticated:
        return redirect('index')
    if not request.user.attendee.is_reviewer:
        return redirect('index')
    paper = get_object_or_404(Paper, pk=pk)
    review = Review.objects.get(paper=paper, reviewer=request.user.attendee)
    if request.POST:
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
        return redirect('index')
    else:
        review_form = ReviewForm(data=model_to_dict(review))
        context = {
            "review": review,
            "review_form": review_form,
            "logged_in_user": request.user.attendee
        }
        return render(request, 'apps/review_update.html', context)


def dashboardPage(request):
    if not request.user.is_authenticated:
        return redirect('index')
    context = {}
    logged_in_user = request.user.attendee
    context['logged_in_user'] = logged_in_user
    # update profile: /attendee/<logged_in_user.id>/update
    # TODO: need update attendee view
    # my papers
    my_papers = Paper.objects.filter(primary_author__exact=logged_in_user.id)
    context['my_submitted_papers'] = my_papers
    # check if user has accepted papers
    has_accepted_papers = len([paper for paper in my_papers if paper.is_accepted]) > 0
    context["has_accepted_papers"] = has_accepted_papers
    # my review tasks
    if logged_in_user.is_reviewer:
        my_review_tasks = []
        all_papers = Paper.objects.all()
        my_reviews = Review.objects.filter(reviewer__exact=logged_in_user.id)
        reviewed_papers = set([r.paper.id for r in my_reviews])
        for paper in all_papers:
            if paper.id in reviewed_papers:
                my_review_tasks.append((paper, True))
            else:
                my_review_tasks.append((paper, False))
        context['my_review_tasks'] = my_review_tasks
    # full list of papers
    return render(request, 'apps/dashboard.html', context)



