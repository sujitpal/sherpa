from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Attendee, Paper, Review

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
    
    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(username__exact=email)
        if user:
            raise ValidationError('Account with this email already exists, please Login using the link below. If you have forgotten your password, click Forgot Password.')


class PaperForm(forms.ModelForm):
    paper_type = forms.ChoiceField(choices=Paper.PAPER_TYPES, required=True, help_text='Choose presentation type')
    title = forms.CharField(max_length=128, required=True, help_text='Enter title for your presentation')
    abstract = forms.CharField(
        widget=forms.Textarea,
        required=True, 
        help_text='Enter abstrct (suggested max 500 words) for presentation')
    keywords = forms.CharField(max_length=128, help_text='Enter keywords for presentation')
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


class ReviewForm(forms.ModelForm):
    paper_choices = Paper.objects.all()
    paper = forms.ModelChoiceField(queryset=paper_choices,
        required=True, help_text='Choose Paper')
    score = forms.ChoiceField(choices=Review.SCORES, 
        required=True, help_text='Enter review score')
    comments = forms.CharField(widget=forms.Textarea, 
        required=False, help_text='Enter review comments (optional)')

    class Meta:
        model = Review
        fields = [
            'paper', 'score', 'comments'
        ]
