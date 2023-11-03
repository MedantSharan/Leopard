from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import Task, User

class TaskTest(TestCase):
    """Unit tests for the Task model."""
    
    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.create_user(
            '@johndoe',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
        )
        self.task = Task(
            title = "Task title",
            description = "Description of the task",
            created_by = self.user,
        )

    def test_valid_task(self):
        try:
            self.task.full_clean()
        except ValidationError:
            self.fail("Test message should be valid")

    def test_must_be_created_by_a_user(self):
        self.task.created_by = None
        with self.assertRaises(ValidationError):
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