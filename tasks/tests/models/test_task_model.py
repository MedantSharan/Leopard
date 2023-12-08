from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.test import TestCase
from tasks.models import Task, User, Team

class TaskTest(TestCase):
    """Unit tests for the Task model."""
    
    fixtures = [
        'tasks/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        
        self.team = Team.objects.create(team_id = 1, 
            team_leader = self.user, 
            team_name ='Test team', 
            team_description = 'This is a test team'
        )
        self.team.team_members.set([self.user])
        
        self.task = Task.objects.create(
            title = "Task title",
            description = "Description of the task",
            created_by = self.user,
            related_to_team = self.team,
            due_date = (datetime.now().date() + timedelta(days=1)),
        )
        self.task.assigned_to.set([self.user])

    def test_valid_task(self):
        try:
            self.task.full_clean()
        except ValidationError:
            self.fail("Test message should be valid")

    def test_must_be_created_by_a_user(self):
        self.task.created_by = None
        with self.assertRaises(ValidationError):
            self.task.full_clean()

    def test_must_be_assigned_to_a_user(self):
        self.task.assigned_to.set([])
        with self.assertRaises(Exception):
            self.task.full_clean()

    def test_title_must_not_be_blank(self):
        self.task.title = ''
        with self.assertRaises(ValidationError):
            self.task.full_clean()

    def test_title_must_not_be_longer_than_100_characters(self):
        self.task.title = 'x' * 101
        with self.assertRaises(ValidationError):
            self.task.full_clean()

    def test_description_must_not_be_blank(self):
        self.task.description = ''
        with self.assertRaises(ValidationError):
            self.task.full_clean()

    def test_description_must_not_be_longet_than_500_characters(self):
        self.task.description = 'x' * 501
        with self.assertRaises(ValidationError):
            self.task.full_clean()

    def test_must_be_related_to_a_team(self):
        self.task.related_to_team = None
        with self.assertRaises(ValidationError):
            self.task.full_clean()

    def test_due_date_can_be_null(self):
        self.task.due_date = None
        try:
            self.task.full_clean()
        except ValidationError:
            self.fail("Due date should be valid")

    