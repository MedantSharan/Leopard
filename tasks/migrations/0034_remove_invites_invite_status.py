# Generated by Django 4.2.6 on 2023-12-07 11:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0033_merge_20231206_1343'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invites',
            name='invite_status',
        ),
    ]
