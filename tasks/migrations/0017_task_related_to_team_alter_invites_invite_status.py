# Generated by Django 4.2.6 on 2023-11-23 15:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0016_alter_invites_invite_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='related_to_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tasks.team'),
        ),
        migrations.AlterField(
            model_name='invites',
            name='invite_status',
            field=models.CharField(choices=[('A', 'Accepted'), ('R', 'Rejected'), ('S', 'Sent')], default='S', max_length=1),
        ),
    ]
