from django.contrib import admin

from .models import Attendee, Paper, Review

# Register your models here.
admin.site.register(Attendee)
admin.site.register(Paper)
admin.site.register(Review)