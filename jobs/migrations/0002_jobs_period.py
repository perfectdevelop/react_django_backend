# Generated by Django 3.1.2 on 2020-11-09 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='period',
            field=models.CharField(default='', max_length=250),
        ),
    ]
