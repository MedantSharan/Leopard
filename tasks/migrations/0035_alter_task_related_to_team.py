# Generated by Django 4.2.6 on 2023-12-07 12:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0034_remove_invites_invite_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='related_to_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_tasks', to='tasks.team'),
        ),
    ]
