from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from datetime import datetime

# Create your models here.

class Attendee(models.Model):
    ORGS = [
        ("LexisNexis", 'LexisNexis'),
        ("Elsevier", 'Elsevier'),
        ("Exhibitions", 'Exhibitions'),
        ("RELX", 'RELX'),
        ("External", 'External')
    ]
    TIMEZONES = [('UTC{:+d}'.format(i), 'UTC{:+d}'.format(i)) for i in range(-12, 12, 1)]

    # gets filled on initial signup
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=True)
    email = models.EmailField(max_length=128, blank=True)
    org = models.CharField(max_length=32, choices=ORGS, default=0)
    timezone = models.CharField(max_length=32, choices=TIMEZONES, default=12)
    # gets filled only when paper accepted
    speaker_bio = models.TextField(blank=True)
    speaker_avatar = models.FileField(upload_to='avatars', blank=True)
    # gets filled automatically (always true)
    is_attendee = models.BooleanField(default=True)
    # gets filled at different stages by admin
    is_reviewer = models.BooleanField(default=False)
    is_speaker = models.BooleanField(default=False)
    is_organizer = models.BooleanField(default=False)

    def __str__(self):
        if self.name == '':
            return '{:s} (signup pending)'.format(self.user.username)
        else:
            return '{:s} ({:s})'.format(self.name, self.org)


@receiver(post_save, sender=User)
def create_user_attendee(sender, instance, created, **kwargs):
    if created:
        Attendee.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_attendee(sender, instance, **kwargs):
    instance.attendee.save()


class Paper(models.Model):
    PAPER_TYPES = [
        (0, 'Long Form'),
        (1, 'Short Form'),
        (3, 'Workshop'),
        (4, 'Poster')
    ]

    # entered by author during submission
    paper_type = models.PositiveSmallIntegerField(choices=PAPER_TYPES, default=0)
    title = models.CharField(max_length=128, blank=False)
    abstract = models.TextField(blank=False)
    keywords = models.CharField(max_length=128, blank=False)
    primary_author = models.ForeignKey(
        'apps.Attendee', related_name='primary_author', on_delete=models.CASCADE)
    co_authors = models.ManyToManyField(Attendee, blank=True)
    submitted_at = models.DateTimeField(default=datetime.now)
    # updated by admin after paper is accepted
    is_accepted = models.BooleanField(default=False)
    # updated by admin for conference schedule
    scheduled_at = models.DateTimeField(default=datetime.now, blank=True)
    # updated by speaker after conference
    pres_slides = models.FileField(upload_to='slides', blank=True)
    pres_videos = models.FileField(upload_to='videos', blank=True)

    def __str__(self):
        return '{:s} ({:s} et al)'.format(
            self.title, self.primary_author.name.split()[-1])


class Review(models.Model):
    SCORES = [
        (0, "Unscored"),
        (1, 'Strong Accept'),
        (2, 'Accept'),
        (3, 'Maybe Accept'),
        (4, 'Reject'),
    ]

    reviewer = models.ForeignKey(
        'apps.Attendee', related_name='reviewer_name', on_delete=models.CASCADE)
    paper = models.ForeignKey(
        'apps.Paper', related_name='paper', on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(choices=SCORES, default=0)
    comments = models.TextField(blank=True)

    def __str__(self):
        return "{:s} / {:s}".format(self.reviewer.name, self.paper.title)
