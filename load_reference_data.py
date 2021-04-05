from apps.models import (
    Organization,
    TimeZone,
    PaperType,
    PaperTheme,
    RejectionReason,
    ReviewScore,
    Event
)

ORG_NAMES = [
    'LexisNexis',
    'Elsevier',
    'Exhibitions',
    'RELX',
    'External'
]
Organization.objects.all().delete()
for org_name in ORG_NAMES:
    org = Organization.objects.create(org_name=org_name)


UTC_OFFSETS = ['UTC{:+d}'.format(i) for i in range(-12, 12, 1)]
TimeZone.objects.all().delete()
for utc_offset in UTC_OFFSETS:
    tz = TimeZone.objects.create(utc_offset=utc_offset)


PAPER_TYPES = [
    'Long Form',
    'Short Form',
    'Workshop',
    'Poster'
]
PaperType.objects.all().delete()
for paper_type_name in PAPER_TYPES:
    pt = PaperType.objects.create(paper_type_name=paper_type_name)


PAPER_THEMES = [
    'Search Algorithms (Text / Boolean)',
    'Search Algorithms (Semantic / Entity based)',
    'Search Algorithms (ML based)',
    'Query Context / Understanding',
    'Search Result Measurement & Evaluation',
    'Techniques applied to Search',
    'Search Infrastructure'
]
PaperTheme.objects.all().delete()
for paper_theme in PAPER_THEMES:
    pt = PaperTheme.objects.create(paper_theme=paper_theme)


REViEW_SCORES = [
    (0, 'Not Reviewed'),
    (4, 'Strong Accept'),
    (3, 'Accept'),
    (2, 'Maybe Accept'),
    (1, 'Reject')
]
ReviewScore.objects.all().delete()
for score, decision in REViEW_SCORES:
    rs = ReviewScore.objects.create(review_score=score, review_decision=decision)


REJECT_REASONS = [
    'Consider Short Form',
    'Consider Workshop',
    'Consider Poster',
    'Other'
]
RejectionReason.objects.all().delete()
for reject_reason in REJECT_REASONS:
    rr = RejectionReason.objects.create(reject_reason=reject_reason)


EVENT_NAMES = [
    (0,  "Signup"),
	(10, "Call for papers"),
	(20, "Review papers"),
	(30, "Paper acceptances sent"),
	(40, "Paper acceptances confirmed"),
	(50, "Schedule created"),
	(60, "Conference"),
	(70, "SSRN submit")
]
Event.objects.all().delete()
for event_seq, event_name in EVENT_NAMES:
    is_current = True if event_seq == 0 else False
    ev = Event.objects.create(
        event_seq=event_seq, event_name=event_name, is_current=is_current)
