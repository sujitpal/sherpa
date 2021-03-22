import os

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from datetime import datetime

# Create your models here.

class Organization(models.Model):
    org_name = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return self.org_name


class TimeZone(models.Model):
    utc_offset = models.CharField(max_length=16, blank=True)

    def __str__(self):
        return self.utc_offset


def _content_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "speaker_{:d}.{:s}".format(instance.id, ext)
    return os.path.join('avatars', filename)
    

class Attendee(models.Model):
    # gets filled on initial signup
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=True)
    email = models.EmailField(max_length=128, blank=True)
    org = models.ForeignKey(
        'apps.Organization', related_name='org', 
        null=True, on_delete=models.CASCADE)
    timezone = models.ForeignKey(
        'apps.TimeZone', related_name='timezone', 
        null=True, on_delete=models.CASCADE)
    interested_in_volunteering = models.BooleanField(default=False)
    interested_in_speaking = models.BooleanField(default=False)
    # gets filled only when paper accepted
    speaker_bio = models.TextField(blank=True)
    speaker_avatar = models.ImageField(upload_to=_content_file_name, blank=True)
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
            return '{:s} ({:s})'.format(self.name, self.org.org_name)


@receiver(post_save, sender=User)
def create_user_attendee(sender, instance, created, **kwargs):
    if created:
        Attendee.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_attendee(sender, instance, **kwargs):
    instance.attendee.save()


class PaperType(models.Model):
    paper_type_name = models.CharField(max_length=16, blank=False)

    def __str__(self):
        return self.paper_type_name


class PaperTheme(models.Model):
    paper_theme = models.CharField(max_length=32, blank=False)

    def __str__(self):
        return self.paper_theme


class Paper(models.Model):
    # entered by author during submission
    paper_type = models.ForeignKey(
        'apps.PaperType', related_name='paper_type', on_delete=models.CASCADE)
    title = models.CharField(max_length=128, blank=False)
    abstract = models.TextField(blank=False)
    themes = models.ManyToManyField(PaperTheme, blank=False)
    keywords = models.CharField(max_length=128, blank=False)
    primary_author = models.ForeignKey(
        'apps.Attendee', related_name='primary_author', on_delete=models.CASCADE)
    co_authors = models.ManyToManyField(Attendee, blank=True)
    submitted_at = models.DateTimeField(default=datetime.now)
    # updated by admin after paper is accepted
    is_accepted = models.BooleanField(default=False)
    # speaker to fill in after paper accepted
    accept_speaker_invite = models.BooleanField(default=False)
    extra_long_paper = models.BooleanField(default=False)
    publish_abstract_in_ssrn = models.BooleanField(default=False)
    publish_full_paper_in_ssrn = models.BooleanField(default=False)
    # updated by admin for conference schedule
    scheduled_at = models.DateTimeField(default=datetime.now, blank=True)
    # updated by speaker after conference
    pres_slides = models.FileField(upload_to='slides', blank=True)
    pres_videos = models.FileField(upload_to='videos', blank=True)

    def __str__(self):
        return '{:s} ({:s} et al)'.format(
            self.title, self.primary_author.name.split()[-1])


class ReviewScore(models.Model):
    review_decision = models.CharField(max_length=16, blank=False)
    review_score = models.IntegerField(default=0)

    def __str__(self):
        return self.review_decision


class RejectionReason(models.Model):
    reject_reason = models.CharField(max_length=32, blank=False)

    def __str__(self):
        return self.reject_reason


class Review(models.Model):
    # create / update review
    reviewer = models.ForeignKey(
        'apps.Attendee', related_name='reviewer_name', on_delete=models.CASCADE)
    paper = models.ForeignKey(
        'apps.Paper', related_name='paper', on_delete=models.CASCADE)
    decision = models.ForeignKey(
        'apps.ReviewScore', related_name='decision', null=True, on_delete=models.CASCADE)
    reason_if_rejected = models.ForeignKey(
        'apps.RejectionReason', related_name='reason_if_rejected',
        null=True, on_delete=models.CASCADE)
    comments = models.TextField(blank=True)

    def __str__(self):
        return "{:s} / {:s}".format(self.reviewer.name, self.paper.title)
