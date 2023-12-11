from django.core.exceptions import ValidationError
from datetime import datetime
from django.test import TestCase
from tasks.models import Task, User, Team, AuditLog

class AuditLogTest(TestCase):
    """Unit tests for the AuditLog model."""
    
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

        self.log = AuditLog.objects.create(
            username = self.user,
            team = self.team,
            task_title = 'test title',
            action = 'create',
            changes = 'test changes'
        )

    def test_valid_audit_log(self):
        try:
            self.log.full_clean()
        except ValidationError:
            self.fail("Audit log should be valid")

    def test_must_be_created_by_a_user(self):
        self.log.username = None
        with self.assertRaises(ValidationError):
            self.log.full_clean()

    def test_must_be_related_to_a_team(self):
        self.log.team = None
        with self.assertRaises(ValidationError):
            self.log.full_clean()

    def test_action_must_not_be_longer_than_100_characters(self):
        self.log.action = 'x' * 101
        with self.assertRaises(ValidationError):
            self.log.full_clean()

    def test_changes_must_not_be_longer_than_1000_characters(self):
        self.log.changes = 'x' * 1001
        with self.assertRaises(ValidationError):
            self.log.full_clean()

    def test_task_title_can_be_null(self):
        self.log.task_title = None
        try:
            self.log.full_clean()
        except ValidationError:
            self.fail("Task title should be allowed to be null")

    def test_timestamp_is_set_on_creation(self):
        self.assertEqual(self.log.timestamp.date(), datetime.now().date())

    def test_changes_can_be_null(self):
        self.log.changes = None
        try:
            self.log.full_clean()
        except ValidationError:
            self.fail("Changes should be allowed to be null")



    