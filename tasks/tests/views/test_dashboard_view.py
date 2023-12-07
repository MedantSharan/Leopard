"""Tests of the dashboard view."""

from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team, Task, Invites

class TeamPageViewTestCase(TestCase):
    """Unit tests of the dashboard view."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username='@janedoe')

        self.team = Team.objects.create(
            team_name='Test team',
            team_description='This is a test team',
            team_leader=self.user
        )
        self.team.team_members.set([self.user])

        self.task = Task.objects.create(
            title='Test task',
            description='This is a test task',
            created_by=self.user,
            related_to_team=self.team,
        )
        self.task.assigned_to.set([self.user])

        self.invite = Invites.objects.create(
            username=self.second_user,
            team_id=self.team.team_id,
        )
    
        self.url = reverse('dashboard')

    def test_dashboard_url(self):
        self.assertEqual(self.url, '/dashboard/')

    def test_get_dashboard(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_get_dashboard_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_invites_displayed(self):
        self.client.login(username=self.second_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('invites', response.context)
        self.assertIn(self.invite, response.context['invites'])

    def test_tasks_displayed(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('tasks', response.context)
        self.assertIn(self.task, response.context['tasks'])

    def test_teams_displayed(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('teams', response.context)
        self.assertIn(self.team, response.context['teams'])

    def test_dashboard_with_query(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?q=Task')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn('tasks', response.context)
        self.assertIn(self.task, response.context['tasks'])

    