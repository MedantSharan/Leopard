"""Tests of the team_page view."""

from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team, Task

class TeamPageViewTestCase(TestCase):
    """Unit tests of the team_page view."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')

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

        self.url = reverse('team_page', kwargs={'team_id': self.team.team_id})

    def test_team_page_url(self):
        self.assertEqual(self.url, f'/team_page/{self.team.team_id}/')

    def test_get_team_page(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team_page.html')

    def test_get_team_page_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_get_team_page_with_invalid_team_id(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(reverse('team_page', kwargs={'team_id': 2}), follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_team_page_with_query(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?q=Task')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team_page.html')
        self.assertIn('query', response.context)
        self.assertEqual(response.context['query'], 'Task')
        self.assertIn('tasks', response.context)

    

