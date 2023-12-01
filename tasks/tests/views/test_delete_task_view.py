"""Tests of the delete_task view."""
from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from tasks.models import User, Task, Team
from tasks.forms import TaskForm

class CreateTaskViewTestCase(TestCase):
    """Unit tests of the delete_task view."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')

        self.team = Team.objects.create(team_id = 1, 
            team_leader = self.user, 
            team_name ='Test team', 
            team_description = 'This is a test team'
        )
        self.team.team_members.set([self.user])

        self.task = Task.objects.create(title = 'Test task',
            description = 'This is a test task',
            created_by = self.user,
            due_date = (datetime.now().date() + timedelta(days=1)),
        )
        self.task.assigned_to.set([self.user])
        self.task.related_to_team = self.team
        self.task.save()

        self.url = reverse('delete_task', kwargs={'task_id': self.task.id})

    def test_delete_task_url(self):
        self.assertEqual(self.url, f'/delete_task/{self.task.id}')

    def test_delete_task(self):
        self.client.login(username=self.user.username, password='Password123')
        session = self.client.session
        session.update({'team': self.team.team_id})
        session.save()
        self.session = session
        before_count = Task.objects.count()
        response = self.client.post(self.url, follow = True)
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count - 1)
        self.assertRedirects(response, reverse('team_page', kwargs={'team_id': self.team.team_id}), status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_page.html')