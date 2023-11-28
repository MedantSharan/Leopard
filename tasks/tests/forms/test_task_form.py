"""Unit tests of the task form."""
from django import forms
from datetime import datetime, timedelta
from django.test import TestCase
from tasks.forms import TaskForm
from tasks.models import Task, User, Team, Team_Members

class TaskFormTestCase(TestCase):
    """Unit tests of the task form."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.team_member = Team_Members.objects.create(team_id = 1, username = self.user)
        self.form_input = {
            'title' : 'Test task',
            'description' : 'This is a test task',
            'assigned_to' : [self.team_member.username.id],
            'due_date' : (datetime.now().date() + timedelta(days=1)),
        }

        self.team = Team.objects.create(team_id = 1, 
            team_leader = self.user, 
            team_name ='Test team', 
            team_description = 'This is a test team'
        )

    def test_form_has_necessary_fields(self):
        form = TaskForm(team_id=1)
        self.assertIn('title', form.fields)
        self.assertIn('description', form.fields)
        description_field = form.fields['description']
        self.assertTrue(isinstance(description_field.widget, forms.Textarea))
        self.assertIn('assigned_to', form.fields)
        assigned_to_field = form.fields['assigned_to']
        self.assertTrue(isinstance(assigned_to_field, forms.ModelMultipleChoiceField))
        self.assertIn('due_date', form.fields)
        due_date_field = form.fields['due_date']
        self.assertTrue(isinstance(due_date_field.widget, forms.DateInput))

    def test_valid_task_form(self):
        form = TaskForm(team_id = 1, data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_invalid_task_form(self):
        self.form_input['title'] = 'x'*101 
        form = TaskForm(team_id = 1, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        testUser = User.objects.get(username='@janedoe')
        task = Task.objects.create(
            title = "Task title",
            description = "Description of the task",
            created_by = testUser,
            related_to_team = self.team,
            due_date = (datetime.now().date() + timedelta(days=2))
        )
        task.assigned_to.set([self.team_member])

        form = TaskForm(team_id = 1, instance=task, data=self.form_input)
        before_count = Task.objects.count()
        form.save()
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(task.title, 'Test task')
        self.assertEqual(task.description, 'This is a test task')
        self.assertEqual(task.created_by, testUser)
        self.assertQuerysetEqual(task.assigned_to.all(), [repr(self.team_member)], transform=repr)
        self.assertEqual(task.related_to_team, self.team)
        self.assertEqual(task.due_date, (datetime.now().date() + timedelta(days=1)))

    def test_due_date_must_be_in_the_future(self):
        self.form_input['due_date'] =  (datetime.now().date() - timedelta(days=1))
        form = TaskForm(team_id = 1, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_due_date_can_be_blank(self):
        self.form_input['due_date'] = ''
        form = TaskForm(team_id = 1, data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_must_be_assigned_to_a_user(self):
        self.form_input['assigned_to'] = []
        form = TaskForm(team_id = 1, data=self.form_input)
        self.assertFalse(form.is_valid())
