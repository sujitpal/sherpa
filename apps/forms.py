from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Attendee, Paper

class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length=128, required=True, help_text='Enter your name')
    email = forms.EmailField(max_length=128, required=True, help_text='Enter your email')
    org = forms.ChoiceField(choices=Attendee.ORGS, required=True, help_text='Choose your organization')
    timezone = forms.ChoiceField(choices=Attendee.TIMEZONES, required=True, help_text='Choose your timezone')
    class Meta:
        model = User
        fields = [
            'name', 'email', 'org', 'timezone',
        ]


class PaperForm(forms.ModelForm):
    paper_type = forms.ChoiceField(choices=Paper.PAPER_TYPES, required=True, help_text='Choose presentation type')
    title = forms.CharField(max_length=128, required=True, help_text='Enter title for your presentation')
    abstract = forms.CharField(
        widget=forms.Textarea,
        required=True, 
        help_text='Enter abstrct (suggested max 500 words) for presentation')
    keywords = forms.CharField(max_length=128, help_text='Enter keywords for presentation')
    # author_choices = tuple([(str(a), str(a)) 
    #     for a in Attendee.objects.exclude(name__exact='')])
    author_choices = Attendee.objects.exclude(name__exact='')
    primary_author = forms.ModelChoiceField(
        queryset=author_choices,
        required=True,
        help_text='Choose primary author'
    )
    co_authors = forms.ModelMultipleChoiceField(
        queryset=author_choices,
        required=False,
        help_text='Add your co-authors, if any'
    )

    class Meta:
        model = Paper
        fields = [
            "paper_type", "title", "abstract", "keywords", 
            "primary_author", "co_authors"
        ]
