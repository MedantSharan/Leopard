# Generated by Django 4.2.6 on 2023-11-28 12:14
# Generated by Django 4.2.6 on 2023-11-27 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0020_alter_invites_invite_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invites',
            name='invite_status',
            field=models.CharField(choices=[('R', 'Rejected'), ('S', 'Sent'), ('A', 'Accepted')], default='S', max_length=1),
        ),
    ]
