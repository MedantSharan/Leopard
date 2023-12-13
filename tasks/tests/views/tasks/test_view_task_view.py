"""Tests of the view_task view."""
from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from tasks.models import User, Task, Team
from tasks.forms import TaskForm

class ViewTaskViewTestCase(TestCase):
    """Unit tests of the view_task view."""

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
            related_to_team = self.team,
            priority = 'low'
        )
        self.task.assigned_to.set([self.user])

        self.url = reverse('view_task', kwargs={'task_id': self.task.id})

    def test_view_task_url(self):
        self.assertEqual(self.url, f'/view_task/{self.task.id}/')

    def test_get_view_task(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_task.html')
        self.assertIn('task', response.context)
        task = response.context['task']
        self.assertEqual(task, self.task)

    def test_get_view_task_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_view_task_with_invalid_task_id(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(reverse('view_task', kwargs={'task_id': 2}), follow = True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
