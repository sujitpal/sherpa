# Run from Django shell (python manage.py shell) using following call.
# >>> exec(open("scripts/submissions_over_time.py").read())

import datetime
import matplotlib.pyplot as plt
import numpy as np

from apps.models import Paper

CFP_OPEN_DATE = datetime.date(2021, 4, 1)
CFP_CLOSE_DATE = datetime.date(2021, 5, 28)
CFP_EXTN_DATE = datetime.date(2021, 6, 11)

papers = Paper.objects.all()
submission_elapsed_days = sorted(
    [(p.submitted_at.date() - CFP_OPEN_DATE).days for p in papers])
# print(submission_elapsed_days)

cumulative_submission_counts = np.cumsum(np.ones(len(submission_elapsed_days)))
# print(cumulative_submission_counts)

plt.plot(submission_elapsed_days, cumulative_submission_counts)
plt.xlabel("number of days after CFP opened")
plt.ylabel("total number of submissions")

plt.axvline(0, ymin=0, ymax=max(cumulative_submission_counts),
            color='g', linestyle='--', label="CFP open")

cfp_close = (CFP_CLOSE_DATE - CFP_OPEN_DATE).days
plt.axvline(cfp_close, ymin=0, ymax=max(cumulative_submission_counts),
            color='r', linestyle='--', label="CFP close")

cfp_extn = (CFP_EXTN_DATE - CFP_OPEN_DATE).days
plt.axvline(cfp_extn, ymin=0, ymax=max(cumulative_submission_counts),
            color='orange', linestyle='--', label="CFP extn")

plt.legend(loc="best")

plt.savefig("scripts/submissions_over_time.png")
