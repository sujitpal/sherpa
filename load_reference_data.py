from apps.models import (
    Organization,
    TimeZone,
    PaperType,
    PaperTheme,
    RejectionReason,
    ReviewScore,
)

ORG_NAMES = [
    'LexisNexis',
    'Elsevier',
    'Exhibitions',
    'RELX',
    'External'
]
for org_name in ORG_NAMES:
    org = Organization.objects.create(org_name=org_name)


UTC_OFFSETS = ['UTC{:+d}'.format(i) for i in range(-12, 12, 1)]
for utc_offset in UTC_OFFSETS:
    tz = TimeZone.objects.create(utc_offset=utc_offset)


PAPER_TYPES = [
    'Long Form',
    'Short Form',
    'Workshop',
    'Poster'
]
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
for paper_theme in PAPER_THEMES:
    pt = PaperTheme.objects.create(paper_theme=paper_theme)


REViEW_SCORES = [
    (0, 'Not Reviewed'),
    (4, 'Strong Accept'),
    (3, 'Accept'),
    (2, 'Maybe Accept'),
    (1, 'Reject')
]
for score, decision in REViEW_SCORES:
    rs = ReviewScore(review_score=score, review_decision=decision)


REJECT_REASONS = [
    'Consider Short Form',
    'Consider Workshop',
    'Consider Poster',
    'Other'
]
for reject_reason in REJECT_REASONS:
    rr = RejectionReason(reject_reason=reject_reason)