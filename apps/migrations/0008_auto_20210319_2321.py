# Generated by Django 3.1.7 on 2021-03-19 23:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0007_auto_20210319_2317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendee',
            name='org',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='org', to='apps.organization'),
        ),
        migrations.AlterField(
            model_name='attendee',
            name='timezone',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timezone', to='apps.timezone'),
        ),
    ]
