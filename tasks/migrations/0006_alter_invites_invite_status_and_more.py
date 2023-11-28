# Generated by Django 4.2.6 on 2023-11-11 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0005_invites_invite_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invites',
            name='invite_status',
            field=models.CharField(choices=[('R', 'Rejected'), ('A', 'Accepted'), ('S', 'Sent')], default='S', max_length=1),
        ),
        migrations.AlterUniqueTogether(
            name='invites',
            unique_together={('team_id', 'username')},
        ),
        migrations.AlterUniqueTogether(
            name='team_members',
            unique_together={('team_id', 'username')},
        ),
    ]