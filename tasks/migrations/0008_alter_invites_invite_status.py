# Generated by Django 4.2.6 on 2023-11-21 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_merge_20231117_1308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invites',
            name='invite_status',
            field=models.CharField(choices=[('S', 'Sent'), ('A', 'Accepted'), ('R', 'Rejected')], default='S', max_length=1),
        ),
    ]
