# Generated by Django 3.1.7 on 2021-03-19 23:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0006_organization_papertheme_papertype_reviewscore_timezone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timezone',
            old_name='timezone',
            new_name='utc_offset',
        ),
    ]
