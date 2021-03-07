from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Attendee

class RegisterForm(UserCreationForm):
    # ORGS = [
    #     (0, 'LexisNexis'),
    #     (1, 'Elsevier'),
    #     (2, 'Exhibitions'),
    #     (3, 'RELX'),
    #     (4, 'External')
    # ]
    # TIMEZONES = [(i + 12, 'UTC{:+d}'.format(i)) for i in range(-12, 12, 1)]

    name = forms.CharField(max_length=128, required=True, help_text="Enter your name")
    email = forms.EmailField(max_length=128, required=True, help_text="Enter your email")
    org = forms.ChoiceField(choices=Attendee.ORGS, required=True, help_text="Choose your organization")
    timezone = forms.ChoiceField(choices=Attendee.TIMEZONES, required=True, help_text="Choose your timezone")
    class Meta:
        model = User
        fields = [
            "name", "email", "org", "timezone",
        ]
