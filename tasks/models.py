from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)


    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)
    

class Team(models.Model):
    team_id = models.BigAutoField(primary_key=True)
    team_leader = models.ForeignKey(User, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=30, blank=False)
    team_description =  models.CharField(
        unique=False,
        blank=True,
        max_length=200,
    ) 
    team_members = models.ManyToManyField(User, related_name = 'member_of_team')


class Invites(models.Model):
    INVITE_STATUS = {
        ("S", "Sent"),
        ("R", "Rejected"),
        ("A", "Accepted"),
    }
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    team_id = models.IntegerField()
    invite_status = models.CharField(max_length=1, choices=INVITE_STATUS, default="S")

    class Meta:
        unique_together = ('team_id', 'username')

class Task(models.Model):
    """Tasks to be set to users"""

    title = models.CharField(max_length = 100)
    description = models.CharField(max_length = 500)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'set_by')
    assigned_to = models.ManyToManyField(User, related_name = 'assigned_tasks')
    related_to_team = models.ForeignKey(Team, on_delete=models.CASCADE, null = True)
    due_date = models.DateField(null = True, blank = True)

    def clean(self):
        super().clean()
        if self.id and not self.assigned_to.exists():
            raise Exception({'assigned_to': 'This task must be assigned to a user'})
