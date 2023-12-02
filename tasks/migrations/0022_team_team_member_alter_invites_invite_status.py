# Generated by Django 4.2.6 on 2023-11-28 16:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0021_remove_team_team_member_alter_invites_invite_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='team_member',
            field=models.ManyToManyField(related_name='member_of_team', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='invites',
            name='invite_status',
            field=models.CharField(choices=[('S', 'Sent'), ('R', 'Rejected'), ('A', 'Accepted')], default='S', max_length=1),
        ),
    ]