from django.core.management.base import BaseCommand, CommandError

from tasks.models import User, Team, Task, Invites, AuditLog

import pytz
from faker import Faker
from random import randint, random

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]


class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    DEFAULT_PASSWORD = 'Password123'
    TASKS_PER_USER = 5
    TEAMS_PER_USER = 10
    INVITES_PER_USER = 10
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()
        self.create_teams()
        self.create_tasks()
        self.create_invites()

    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})
       
    def try_create_user(self, data):
        try:
            self.create_user(data)
        except:
            pass

    def create_user(self, data):
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )
        if data['username'] == '@johndoe':
            user.is_superuser = True
            user.is_staff = True
            user.save()

    def create_teams(self):
        for user in User.objects.all():
            if user.username != '@johndoe':
                for i in range(randint(1, self.TEAMS_PER_USER)):
                    team_leader = self.users.exclude(id=user.id).exclude(username='@johndoe').order_by('?').first()
                    team = Team.objects.create(
                        team_leader=team_leader,
                        team_name=self.faker.word(),
                        team_description=self.faker.sentence(),
                    )
                    team.team_members.add(team_leader)
                    team.team_members.add(user)
            else:
                team = Team.objects.create(
                    team_leader=user,
                    team_name="Seeded team",
                    team_description="This team is seeded as required",
                )
                team.team_members.add(user)
                team.team_members.add(User.objects.get(username='@janedoe'))
                team.team_members.add(User.objects.get(username='@charlie'))
            print(f"Seeding teams", end='\r')
        print("Team seeding complete.      ")

    def create_tasks(self):
        for team in Team.objects.all():
            for user in team.team_members.all():
                for i in range(randint(1, self.TASKS_PER_USER)):
                    task = Task.objects.create(
                        title=self.faker.sentence(),
                        description=self.faker.sentence(),
                        created_by=user,
                        related_to_team=team,
                        due_date=self.faker.date_time_between(start_date='+10y', end_date='+100y', tzinfo=pytz.UTC),
                        priority=Task.PRIORITY_CHOICES[randint(0, 3)][0],
                    )
                    task.assigned_to.add(user)

                    AuditLog.objects.create(
                        username=user,
                        team=team,
                        task_title=task.title,
                        action='Created',
                    )
            print(f"Seeding tasks", end='\r')
        print("Task seeding complete.      ")

    def create_invites(self):
        for user in User.objects.all():
            for i in range(randint(1, self.INVITES_PER_USER)):
                team = Team.objects.all().order_by('?').first()
                if not Invites.objects.filter(team_id=team.team_id, username=user).exists():
                    invite = Invites.objects.create(
                        username=user,
                        team_id=team.team_id,
                    )
            print(f"Seeding invites", end='\r')
        print("Invite seeding complete.      ")

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'


