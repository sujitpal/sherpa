# Generated by Django 3.1.7 on 2021-03-19 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0009_auto_20210319_2323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='org_name',
            field=models.CharField(default='Elsevier', max_length=32),
        ),
    ]