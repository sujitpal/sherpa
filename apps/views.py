import collections
import operator
from plotly.offline import plot
import plotly.graph_objs as go

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Q
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, render, redirect
from django.template.defaulttags import register

from .forms import (
    RegisterForm, 
    ProfileForm,
    SpeakerForm,
    PaperForm, 
    PaperAcceptedForm,
    ReviewForm
)
from .models import (
    Organization,
    TimeZone,
    Attendee, 
    PaperType,
    PaperTheme,
    Paper, 
    ReviewScore,
    Review,
    Event,
)


def _is_speaker(attendee):
    # check if attendee has any papers that are accepted
    num_papers_accepted = Paper.objects.filter(
        Q(primary_author__exact=attendee) | Q(co_authors__id=attendee.id),
        is_accepted=True).count()
    return num_papers_accepted > 0


def _get_logged_in_user(request):
    logged_in_user = None
    if request.user.is_authenticated:
        logged_in_user = request.user.attendee
    return logged_in_user


def _get_star_rating(paper, user):
    review = Review.objects.filter(reviewer__exact=user,
                                   paper__exact=paper.id).first()
    star_rating = 0
    if review is not None:
        star_rating = review.decision.review_score
    return star_rating


def _convert_to_freq_table(values, keys=[], utc_sort=False):
    freqs = {}
    if len(keys) > 0:
        freqs = {k:0 for k in keys}
    for val in values:
        if val in freqs.keys():
            freqs[val] += 1
        else:
            freqs[val] = 1
    if utc_sort:
        value_counts = sorted(freqs.items(), key=lambda k: int(k[0].replace("UTC", "")))
    else:
        value_counts = sorted(freqs.items(), key=operator.itemgetter(0))
    return value_counts


def _sum_value_counts(value_counts):
    return sum([c for v, c in value_counts])


def _generate_pie_chart(value_counts, chart_title):
    values = [vc[0] for vc in value_counts]
    counts = [vc[1] for vc in value_counts]
    fig = go.Figure()
    pie = go.Pie(values=counts, labels=values,
        hole=0.5, showlegend=True, name=chart_title)
    fig.update_layout(autosize=False,
        width=300, height=300,
        margin=dict(l=50, r=50, b=50, t=50, pad=4))
    fig.add_trace(pie)
    plt_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plt_div


def _generate_bar_chart(value_counts, chart_title):
    values = [vc[0] for vc in value_counts]
    counts = [vc[1] for vc in value_counts]
    fig = go.Figure()
    bar = go.Bar(x=counts, y=values,
        showlegend=False, name=chart_title,
        orientation='h')
    fig.update_layout(autosize=False,
        width=300, height=600,
        margin=dict(l=50, r=50, b=50, t=50, pad=4),
        template='plotly_white')
    fig.add_trace(bar)
    plt_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plt_div


def _get_current_event():
    return (Event.objects.filter(is_current=True)
        .order_by('-event_seq')
        .first()
        .event_seq)


# Create your views here.

def indexPage(request):
    # # This page should never be visible, replace all redirect('index')
    # # calls to redirect('user_portal') defined below
    # context = {}
    # if request.user.is_authenticated:
    #     context["logged_in_user"] = _get_logged_in_user(request)
    # return render(request, 'apps/index.html', context)
    return redirect('dashboard')


def signUpPage(request):
    context = {}
    if request.POST:
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # extract form fields
            password = form.cleaned_data.get('password1')
            # update user
            name = form.cleaned_data.get('name')
            email_address = form.cleaned_data.get('email_address')
            org = form.cleaned_data.get('org')
            timezone = form.cleaned_data.get('timezone')
            volunteer_interest = form.cleaned_data.get('interested_in_volunteering')
            speaking_interest = form.cleaned_data.get('interested_in_speaking')
            user.username = email_address
            try:
                user.save()
                user.email = email_address
                if not user.attendee:
                    user.attendee = Attendee.objects.get(user=user)
                user.attendee.name = name
                user.attendee.email = email_address
                user.attendee.org = org
                user.attendee.timezone = timezone
                user.attendee.interested_in_volunteering = volunteer_interest
                user.attendee.interested_in_speaking = speaking_interest
                user.save()
                user.attendee.save()
                # authenticate and login
                user = authenticate(username=email_address, password=password)
                login(request, user)
                return redirect('dashboard')
            except Exception:
                form.add_error('email_address', "Email Address already registered!")
                context["signup_form"] = form
        else:
            context["signup_form"] = form
    else:
        form = RegisterForm()
        context["signup_form"] = form
    return render(request, 'apps/signup.html', context)


def signInPage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Error: Wrong Username and/or Password!')
    return render(request, 'apps/signin.html')


def signOutPage(request):
    logout(request)
    return redirect('sign_in')


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
        "logged_in_user": _get_logged_in_user(request)
    }
    return render(request, "apps/attendees.html", context)


def attendeeProfilePage(request):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    if request.POST:
        form = ProfileForm(request.POST, instance=request.user.attendee)
        if form.is_valid():
            form.save()
        return redirect('dashboard')
    else:
        initial_data = {
            'name': request.user.attendee.name,
            'email_address': request.user.attendee.email,
            'org': request.user.attendee.org,
            'timezone': request.user.attendee.timezone,
            'interested_in_volunteering': request.user.attendee.interested_in_volunteering,
            'interested_in_speaking': request.user.attendee.interested_in_speaking
        }
        form = ProfileForm(initial=initial_data)
        context = {
            "profile_form": form,
            "logged_in_user": _get_logged_in_user(request)
        }
        return render(request, 'apps/attendee_profile_update.html', context)


def attendeeSpeakerUpdatePage(request):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    if not _is_speaker(request.user.attendee):
        return redirect('dashboard')
    if request.POST:
        speaker = request.user.attendee
        form = SpeakerForm(request.POST, request.FILES, instance=speaker)
        if form.is_valid():
            form.save()
        return redirect('dashboard')
    else:
        initial_data = {
            'speaker_bio': request.user.attendee.speaker_bio,
            'speaker_avatar': request.user.attendee.speaker_avatar
        }
        form = SpeakerForm(initial=initial_data)
        context = {
            "speaker_form": form,
            "logged_in_user": _get_logged_in_user(request)
        }
        return render(request, 'apps/attendee_speakerbio_update.html', context)


def attendeeSpeakerViewPage(request, pk):
    speaker = get_object_or_404(Attendee, pk=pk)
    if not _is_speaker(speaker):
        return redirect('dashboard')
    context = {
        "speaker": speaker,
        "logged_in_user": _get_logged_in_user(request)
    }
    return render(request, "apps/attendee_speakerbio_view.html", context)


def attendeeStatsPage(request):
    attendees_by_org = [a.org.org_name for a in Attendee.objects.exclude(name__exact='')]
    attendees_by_org = _convert_to_freq_table(attendees_by_org)
    attendees_by_org_total = _sum_value_counts(attendees_by_org)
    attendees_by_org_pie = _generate_pie_chart(attendees_by_org, 'Attendees by Organization')

    attendees_by_tz = [a.timezone.utc_offset for a in Attendee.objects.exclude(name__exact='')]
    all_tzs = [tz.utc_offset for tz in TimeZone.objects.all()]
    attendees_by_tz = _convert_to_freq_table(attendees_by_tz, keys=all_tzs, utc_sort=True)
    attendees_by_tz_total = _sum_value_counts(attendees_by_tz)
    attendees_by_tz_bar = _generate_bar_chart(attendees_by_tz, 'Attendees by Timezone')

    context = {
        'attendees_by_org': attendees_by_org,
        'attendees_by_org_total': attendees_by_org_total,
        'attendees_by_org_pie': attendees_by_org_pie,
        'attendees_by_tz': filter(lambda x: x[1] > 0, attendees_by_tz),
        'attendees_by_tz_total': attendees_by_tz_total,
        'attendees_by_tz_bar': attendees_by_tz_bar,
        'logged_in_user': _get_logged_in_user(request)
    }
    return render(request, 'apps/attendee_stats.html', context)


def paperCreatePage(request):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    if request.POST:
        form = PaperForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('dashboard')
    else:
        form = PaperForm(initial={
            'primary_author': request.user.attendee.id,
        })
        form.fields['co_authors'].queryset = (Attendee.objects
            .exclude(name__exact='')
            .exclude(id=request.user.attendee.id))
        context = {
            'paper_form': form,
            'logged_in_user': _get_logged_in_user(request)
        }
        return render(request, "apps/paper_create.html", context)


def paperRetrievePage(request, pk):
    paper = get_object_or_404(Paper, pk=pk)
    # if user is author or co-author, they should be able to access
    # if user is organizer then they should be able to access
    # once paper is accepted, everyone should be able to access
    if ((request.user.is_authenticated and (
            request.user.attendee == paper.primary_author or 
            request.user.attendee in paper.co_authors.all() or 
            request.user.attendee.is_organizer)) or 
            paper.is_accepted):
        paper_coauthors = ", ".join([ca.name for ca in paper.co_authors.all()])
        themes = PaperTheme.objects.filter(paper=paper)
        paper.themes.set(themes)
        context = {
            "paper": paper,
            'paper_themes': themes,
            "paper_author": paper.primary_author.name,
            "paper_coauthors": paper_coauthors,
            "logged_in_user": _get_logged_in_user(request)
        }
        return render(request, 'apps/paper.html', context)
    else:
        return redirect('dashboard')


def paperUpdatePage(request, pk):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    paper = get_object_or_404(Paper, pk=pk)
    if request.POST:
        form = PaperForm(request.POST, instance=paper)
        if form.is_valid():
            form.save()
        return redirect('dashboard')
    else:
        form = PaperForm(data=model_to_dict(paper))
        context = {
            "paper_id": paper.id,
            "paper_form": form,
            "logged_in_user": _get_logged_in_user(request)
        }
        return render(request, 'apps/paper_update.html', context)


def paperDeletePage(request, pk):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    context = {}
    paper = get_object_or_404(Paper, pk=pk)
    if request.POST:
        paper.delete()
        return redirect('dashboard')
    return render(request, 'apps/paper_delete.html', context)


def paperListPage(request):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    if not request.user.attendee.is_organizer:
        return redirect('dashboard')
    paper_list = Paper.objects.all().order_by('id')
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
        "logged_in_user": _get_logged_in_user(request)
    }
    return render(request, 'apps/papers.html', context)


def paperAcceptedPage(request, pk):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    paper = get_object_or_404(Paper, pk=pk)
    if request.POST:
        form = PaperAcceptedForm(request.POST, instance=paper)
        if form.is_valid():
            form.save()
        return redirect('dashboard')
    else:
        form = PaperAcceptedForm(data=model_to_dict(paper))
        context = {
            'paper': paper,
            'paper_form': form,
            'logged_in_user': _get_logged_in_user(request)
        }
        return render(request, 'apps/paper_accept.html', context)


def paperStatsPage(request):
    papers_by_type = [p.paper_type.paper_type_name 
        for p in Paper.objects.all()]
    papers_by_type = _convert_to_freq_table(papers_by_type)
    papers_by_type_totals = _sum_value_counts(papers_by_type)
    papers_by_type_pie = _generate_pie_chart(papers_by_type, 'Papers by Paper Type')

    paper_author_orgs = [p.primary_author.org.org_name 
        for p in Paper.objects.all()]
    papers_by_org = _convert_to_freq_table(paper_author_orgs)
    papers_by_org_totals = _sum_value_counts(papers_by_org)
    papers_by_org_pie = _generate_pie_chart(papers_by_org, 'Papers by Organization')

    papers_by_theme = []
    for p in Paper.objects.all():
        papers_by_theme.extend([theme.paper_theme for theme in p.themes.all()])
    papers_by_theme = _convert_to_freq_table(papers_by_theme)
    papers_by_theme_totals = _sum_value_counts(papers_by_theme)
    papers_by_theme_pie = _generate_pie_chart(papers_by_theme, 'Papers by Theme')

    paper_author_tzs = [p.primary_author.timezone.utc_offset 
        for p in Paper.objects.all()]
    all_tzs = [tz.utc_offset for tz in TimeZone.objects.all()]
    papers_by_tz = _convert_to_freq_table(paper_author_tzs, keys=all_tzs, utc_sort=True)
    papers_by_tz_totals = _sum_value_counts(papers_by_tz)
    papers_by_tz_bar = _generate_bar_chart(papers_by_tz, 'Papers by Timezone')

    context = {
        'papers_by_type': papers_by_type,
        'papers_by_type_totals': papers_by_type_totals,
        'papers_by_type_pie': papers_by_type_pie,
        'papers_by_org': papers_by_org,
        'papers_by_org_totals': papers_by_org_totals,
        'papers_by_org_pie': papers_by_org_pie,
        'papers_by_theme': papers_by_theme,
        'papers_by_theme_totals': papers_by_theme_totals,
        'papers_by_theme_pie': papers_by_theme_pie,
        'papers_by_tz': papers_by_tz,
        'papers_by_tz_totals': papers_by_tz_totals,
        'papers_by_tz_bar': papers_by_tz_bar,
        'logged_in_user': _get_logged_in_user(request),
        'current_event': _get_current_event()
    }
    return render(request, 'apps/paper_stats.html', context)


def paperAcceptedListPage(request):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    if not request.user.attendee.is_organizer:
        return redirect('dashboard')
    paper_list = Paper.objects.filter(is_accepted=True).order_by('id')
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
        "logged_in_user": _get_logged_in_user(request)
    }
    return render(request, 'apps/papers_accepted.html', context)


def reviewCreatePage(request, pk):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    if not request.user.attendee.is_reviewer:
        return redirect('dashboard')
    paper = get_object_or_404(Paper, pk=pk)
    paper_themes = "; ".join([pt.paper_theme for pt in paper.themes.all()])
    if request.POST:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review_form = form.save(commit=False)
            review_form.reviewer = request.user.attendee
            review_form.paper = paper
            review_form.save()
        return redirect('dashboard')
    else:
        init_data = {
            "reviewer": request.user.attendee,
            "paper": paper,
            "paper_themes": paper_themes
        }
        form = ReviewForm(initial=init_data)
        context = {
            "review_form": form,
            "init_data": init_data,
            "logged_in_user": _get_logged_in_user(request)
        }
        return render(request, "apps/review_create.html", context)


def reviewRetrievePage(request, pk, ak=None):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    if not request.user.attendee.is_reviewer:
        return redirect('dashboard')
    paper = get_object_or_404(Paper, pk=pk)
    paper_themes = "; ".join([pt.paper_theme for pt in paper.themes.all()])
    if ak is None:
        # this is how its called from my reviews (user is signed-in user)
        review = Review.objects.get(paper=paper, reviewer=request.user.attendee)
    else:
        # this is how its called from reviewer details page, attendee key
        # is passed in on URL
        reviewer = get_object_or_404(Attendee, pk=ak)
        review = Review.objects.get(paper=paper, reviewer=reviewer)
    star_rating = range(review.decision.review_score)
    context = {
        "review": review,
        "paper_themes": paper_themes,
        "logged_in_user": _get_logged_in_user(request),
        "star_rating": star_rating,
        "ak_provided": True if ak is not None else False,
    }
    return render(request, 'apps/review.html', context)


def reviewUpdatePage(request, pk):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    if not request.user.attendee.is_reviewer:
        return redirect('dashboard')
    paper = get_object_or_404(Paper, pk=pk)
    paper_themes = "; ".join([pt.paper_theme for pt in paper.themes.all()])
    review = Review.objects.get(paper=paper, reviewer=request.user.attendee)
    if request.POST:
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
        return redirect('dashboard')
    else:
        review_form = ReviewForm(data=model_to_dict(review))
        context = {
            "review": review,
            "paper_themes": paper_themes,
            "review_form": review_form,
            "logged_in_user": request.user.attendee
        }
        return render(request, 'apps/review_update.html', context)


def reviewerStats(request):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    if not request.user.attendee.is_organizer:
        return redirect('dashboard')
    reviewers = Attendee.objects.filter(is_reviewer=True).order_by('name')
    num_papers = Paper.objects.all().count()
    review_stats = []
    for reviewer in reviewers:
        num_reviewed = Review.objects.filter(reviewer=reviewer).count()
        print('reviewer counts:', reviewer, num_reviewed)
        pct_reviewed = 100 * num_reviewed / num_papers
        review_stats.append((reviewer, num_reviewed, pct_reviewed))
    context = {
        "review_stats": review_stats,
        "logged_in_user": request.user.attendee
    }
    return render(request, 'apps/reviewer_stats.html', context)


def _generate_histogram(raw_scores, all_scores,
                        chart_title, paper_count, nbins=4):
    value_counts = {}
    for v in range(1, nbins+1):
        value_counts[v] = len([s for s in raw_scores if s == v])
    score_values = [v for v, _ in value_counts.items()]
    score_counts = [(100 * c / paper_count) for _, c in value_counts.items()]
    fig = go.Figure()
    bar = go.Bar(x=score_values, y=score_counts,
                 name=chart_title,
                 orientation='v')
    all_values = [v for v, _ in all_scores]
    all_counts = [c for _, c in all_scores]
    line = go.Scatter(x=all_values, y=all_counts,
                      name="Overall Reviews")
    fig.update_layout(autosize=False,
                      width=600, height=300,
                      margin=dict(l=50, r=50, b=50, t=50, pad=4),
                      template='plotly_white')
    fig.update_xaxes(type='category', title_text='rating')
    fig.update_yaxes(title_text='percent count')
    fig.add_trace(bar)
    fig.add_trace(line)
    plt_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plt_div


def reviewerDetail(request, pk):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    if not request.user.attendee.is_organizer:
        return redirect('dashboard')
    # compute stats and list for reviewer
    reviewer = get_object_or_404(Attendee, pk=pk)
    all_papers = Paper.objects.all()
    reviewed_papers = set([rp.paper.id for rp in
                           Review.objects.filter(reviewer=reviewer)])
    papers_reviewed_disp, scores = [], []
    for paper in all_papers:
        if paper.id in reviewed_papers:
            star_rating = _get_star_rating(paper, reviewer)
            papers_reviewed_disp.append((paper, True, range(star_rating)))
            scores.append(star_rating)
        else:
            papers_reviewed_disp.append((paper, False, None))
    papers_reviewed_disp = sorted(papers_reviewed_disp,
                                  key=lambda x: x[0].title)
    # compute stats across full set of reviews
    num_reviews = Review.objects.count()
    all_review_counts = (
        Review.objects.all().exclude(decision__review_score=0)
        .values("decision__review_score")
        .annotate(Count("paper")))
    norm_counts = []
    for qs in all_review_counts:
        norm_counts.append((
            qs["decision__review_score"],
            100 * qs["paper__count"] / num_reviews)
        )
    norm_counts = sorted(norm_counts, key=operator.itemgetter(0))
    reviewer_hist = _generate_histogram(scores, norm_counts,
                                        reviewer.name, len(reviewed_papers))
    context = {
        "reviewer_hist": reviewer_hist,
        "reviewer": reviewer,
        "papers_reviewed": papers_reviewed_disp,
        "logged_in_user": request.user.attendee
    }
    return render(request, 'apps/reviewer.html', context)


def dashboardPage(request):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    context = {}
    logged_in_user = request.user.attendee
    context['logged_in_user'] = _get_logged_in_user(request)
    context["current_event"] = _get_current_event()
    # my papers
    my_papers = (
        Paper.objects.
        filter(primary_author__exact=logged_in_user.id).
        order_by('title')
    )
    if len(my_papers) > 0:
        context['has_submitted_papers'] = True
        context['my_submitted_papers'] = my_papers
        # check if user has accepted papers
        has_accepted_papers = len([paper for paper in my_papers
                                   if paper.is_accepted]) > 0
        context["has_accepted_papers"] = has_accepted_papers
    # my review tasks
    if logged_in_user.is_reviewer:
        my_review_task_dict = collections.defaultdict(list)
        all_papers = Paper.objects.all()
        my_reviews = Review.objects.filter(reviewer__exact=logged_in_user.id)
        reviewed_papers = set([r.paper.id for r in my_reviews])
        for paper in all_papers:
            paper_type = paper.paper_type.paper_type_name
            if paper.id in reviewed_papers:
                star_rating = _get_star_rating(paper, logged_in_user)
                my_review_task_dict[paper_type].append(
                    (paper, True, range(star_rating)))
            else:
                my_review_task_dict[paper_type].append((paper, False, None))
        my_review_paper_types = sorted(list(my_review_task_dict.keys()))
        my_review_tasks = []
        for paper_type in my_review_paper_types:
            my_review_tasks.append((
                paper_type, 
                sorted(my_review_task_dict[paper_type],
                       key=lambda x: x[0].title)))
        context['my_review_tasks'] = my_review_tasks

    # full list of papers
    return render(request, 'apps/dashboard.html', context)

