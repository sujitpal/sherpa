# Run from Django shell (python manage.py shell) using following call.
# >>> exec(open("scripts/find_attendees_with_one_name.py").read())

from apps.models import Attendee

fout = open("scripts/attendees-with-one-name.tsv", "w")

num_found = 0
fout.write("id|email|name\n")
for attendee in Attendee.objects.all():
    has_one_name = True if len(attendee.name.strip().split()) == 1 else False
    if has_one_name:
        fout.write("{:d}|{:s}|{:s}\n".format(
            attendee.id, attendee.email, attendee.name))
        num_found += 1

fout.close()
print("{:d} entries found".format(num_found))
