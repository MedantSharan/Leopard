# Generated by Django 4.2.6 on 2023-12-02 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0029_merge_20231202_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invites',
            name='invite_status',
            field=models.CharField(choices=[('S', 'Sent'), ('R', 'Rejected'), ('A', 'Accepted')], default='S', max_length=1),
        ),
    ]
