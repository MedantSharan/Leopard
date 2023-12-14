"""Tests of the update_task_completion view."""
from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from tasks.models import User, Task, Team, AuditLog
from tasks.forms import TaskForm

class UpdateTaskCompletionViewTestCase(TestCase):
    """Unit tests of the update_task_completion view."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username='@janedoe')

        self.form_input = {
            'completed' : 'on'
        }

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

        self.url = reverse('task_completion', kwargs={'task_id': self.task.id})

    def test_update_task_completion_url(self):
        self.assertEqual(self.url, f'/task_completion/{self.task.id}/')

    def test_update_task_completion_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url)

    def test_post_update_task_completion(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team_page.html')
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)

    def test_update_task_completion_redirects_with_invalid_task_id(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(reverse('task_completion', kwargs={'task_id': 2}), self.form_input, follow=True)
        self.assertRedirects(response, reverse('dashboard'))

    def test_update_task_completion_redirects_with_user_not_in_team(self):
        self.client.login(username=self.second_user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response, reverse('dashboard'))

    def test_update_task_completion_redirects_when_user_not_assigned(self):
        self.client.login(username=self.second_user.username, password='Password123')
        self.team.team_members.add(self.second_user)
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response, reverse('team_page', kwargs={'team_id': self.team.team_id}))

    def test_task_creator_can_set_completion(self):
        self.client.login(username=self.user.username, password='Password123')
        self.task.assigned_to.set([self.second_user])
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team_page.html')
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)