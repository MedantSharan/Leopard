# Generated by Django 4.2.6 on 2023-11-22 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0012_alter_invites_invite_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invites',
            name='invite_status',
            field=models.CharField(choices=[('R', 'Rejected'), ('A', 'Accepted'), ('S', 'Sent')], default='S', max_length=1),
        ),
    ]