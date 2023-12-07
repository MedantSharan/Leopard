"""Tests of the delete_task view."""
from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from tasks.models import User, Task, Team
from tasks.forms import TaskForm

class DeleteTaskViewTestCase(TestCase):
    """Unit tests of the delete_task view."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username='@janedoe')

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
        )
        self.task.assigned_to.set([self.user])

        self.url = reverse('delete_task', kwargs={'task_id': self.task.id})

    def test_delete_task_url(self):
        self.assertEqual(self.url, f'/delete_task/{self.task.id}/')

    def test_delete_task(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Task.objects.count()
        response = self.client.post(self.url, follow = True)
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count - 1)
        self.assertRedirects(response, reverse('team_page', kwargs={'team_id': self.team.team_id}), status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_page.html')

    def test_delete_task_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_cannot_delete_task_if_not_creator(self):
        self.client.login(username=self.second_user.username, password='Password123')
        before_count = Task.objects.count()
        response = self.client.post(self.url, follow = True)
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, reverse('team_page', kwargs={'team_id': self.team.team_id}), status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_page.html')
        self.assertIn(self.task, Task.objects.all())

    def test_delete_task_with_invalid_task_id(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(reverse('delete_task', kwargs={'task_id': 2}), follow = True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')