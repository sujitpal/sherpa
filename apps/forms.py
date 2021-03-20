from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    Organization,
    TimeZone,
    Attendee, 
    PaperType,
    PaperTheme,
    Paper, 
    ReviewScore,
    RejectionReason,
    Review
)

class RegisterForm(UserCreationForm):
    name = forms.CharField(
        max_length=128, 
        required=True, 
        help_text='Enter your name')
    email_address = forms.EmailField(
        max_length=128, 
        required=True, 
        help_text='Enter your email')
    org = forms.ModelChoiceField(
        queryset=Organization.objects.all(), 
        required=True, 
        help_text='Choose your organization')
    timezone = forms.ModelChoiceField(
        queryset=TimeZone.objects.all(), 
        required=True, 
        help_text='Choose your timezone')
    interested_in_volunteering = forms.BooleanField(
        required=False,
        help_text='Check box if interested in volunteering for Summit')
    interested_in_speaking = forms.BooleanField(
        required=False,
        help_text='Check box if interested in speaking at Summit')

    class Meta:
        model = User
        fields = [
            'name', 'email_address', 'org', 'timezone',
            'interested_in_volunteering', 'interested_in_speaking'
        ]
    
    def clean_email(self):
        email_address = self.cleaned_data['email_address']
        user = User.objects.filter(username__exact=email_address)
        if user:
            raise ValidationError('Account with this email already exists, please Login using the link below. If you have forgotten your password, click Forgot Password.')


class ProfileForm(forms.ModelForm):
    name = forms.CharField(
        max_length=128, 
        required=True, 
        help_text='Enter your name')
    email_address = forms.EmailField(
        max_length=128, 
        required=True, 
        help_text='Enter your email')
    org = forms.ModelChoiceField(
        queryset=Organization.objects.all(), 
        required=True, 
        help_text='Choose your organization')
    timezone = forms.ModelChoiceField(
        queryset=TimeZone.objects.all(), 
        required=True, 
        help_text='Choose your timezone')
    interested_in_volunteering = forms.BooleanField(
        required=False,
        help_text='Check box if interested in volunteering for Summit')
    interested_in_speaking = forms.BooleanField(
        required=False,
        help_text='Check box if interested in speaking at Summit')

    class Meta:
        model = Attendee
        fields = [
            'name', 'email_address', 'org', 'timezone',
            'interested_in_volunteering', 'interested_in_speaking'
        ]


class SpeakerForm(forms.ModelForm):
    speaker_bio = forms.CharField(
        widget=forms.Textarea,
        required=True,
        help_text='Enter speaker bio (suggested max 250 words)'
    )
    speaker_avatar = forms.FileField()
    class Meta:
        model = Attendee
        fields = [ 
            'speaker_bio', 'speaker_avatar'
        ]


class PaperForm(forms.ModelForm):
    paper_type = forms.ModelChoiceField(
        queryset=PaperType.objects.all(), 
        required=True, 
        help_text='Choose presentation type')
    title = forms.CharField(
        max_length=128, 
        required=True, 
        help_text='Enter title for your presentation')
    abstract = forms.CharField(
        widget=forms.Textarea,
        required=True, 
        help_text='Enter abstract for presentation (suggested max 500 words)')
    themes = forms.ModelMultipleChoiceField(
        queryset=PaperTheme.objects.all(),
        required=True,
        help_text='Choose one or more themes for your paper')
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
            "paper_type", "title", "abstract", 
            'themes', "keywords", 
            "primary_author", "co_authors"
        ]


class ReviewForm(forms.ModelForm):
    paper_choices = Paper.objects.all()
    decision = forms.ModelChoiceField(
        queryset=ReviewScore.objects.all(), 
        required=True, 
        help_text='Enter review score')
    reason_if_rejected = forms.ModelChoiceField(
        queryset=RejectionReason.objects.all(),
        required=False,
        help_text='Reasons for rejection (if rejected)')
    comments = forms.CharField(widget=forms.Textarea, 
        required=False, help_text='Enter review comments (optional)')

    class Meta:
        model = Review
        fields = [
            'decision', 
            'reason_if_rejected',
            'comments'
        ]
