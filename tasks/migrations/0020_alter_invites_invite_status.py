# Generated by Django 4.2.6 on 2023-11-28 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0019_alter_invites_invite_status_remove_task_assigned_to_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invites',
            name='invite_status',
            field=models.CharField(choices=[('A', 'Accepted'), ('S', 'Sent'), ('R', 'Rejected')], default='S', max_length=1),
        ),
    ]
# Generated by Django 4.2.6 on 2023-11-27 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0019_alter_invites_invite_status_remove_task_assigned_to_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invites',
            name='invite_status',
            field=models.CharField(choices=[('A', 'Accepted'), ('S', 'Sent'), ('R', 'Rejected')], default='S', max_length=1),
        ),
    ]
