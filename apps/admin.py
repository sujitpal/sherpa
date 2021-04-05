from django.contrib import admin

from .models import (
    Organization,
    TimeZone,
    Attendee, 
    PaperType,
    PaperTheme,
    Paper, 
    ReviewScore,
    RejectionReason,
    Review,
    Event,
)

# Register your models here.
admin.site.register(Organization)
admin.site.register(TimeZone)
admin.site.register(Attendee)
admin.site.register(PaperType)
admin.site.register(PaperTheme)
admin.site.register(Paper)
admin.site.register(ReviewScore)
admin.site.register(RejectionReason)
admin.site.register(Review)
admin.site.register(Event)
