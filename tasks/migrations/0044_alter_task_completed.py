# Generated by Django 4.2.6 on 2023-12-14 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0043_task_completed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='completed',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
