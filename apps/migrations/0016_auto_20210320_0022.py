# Generated by Django 3.1.7 on 2021-03-20 00:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0015_auto_20210320_0013'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='score',
        ),
        migrations.AddField(
            model_name='review',
            name='decision',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='decision', to='apps.reviewscore'),
        ),
    ]