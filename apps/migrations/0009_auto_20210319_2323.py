# Generated by Django 3.1.7 on 2021-03-19 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0008_auto_20210319_2321'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='interested_in_speaking',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='attendee',
            name='interested_in_volunteering',
            field=models.BooleanField(default=False),
        ),
    ]
