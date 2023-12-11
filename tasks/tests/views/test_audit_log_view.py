"""Tests of the audit_log view."""

from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team, Task, AuditLog

class AuditLogViewTestCase(TestCase):
    """Unit tests of the audit_log view."""

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

        self.log = AuditLog.objects.create(
            username = self.user,
            team = self.team,
            task_title = 'test title',
            action = 'create',
            changes = 'test changes'
        )
    
        self.url = reverse('audit_log', kwargs={'team_id': self.team.team_id})

    def test_audit_log_url(self):
        self.assertEqual(self.url, f'/audit_log/{self.team.team_id}/')

    def test_get_audit_log(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'audit_log.html')

    def test_get_audit_log_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_audit_log_displayed(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('logs', response.context)
        self.assertEqual(len(response.context['logs']), 1)
        self.assertEqual(response.context['logs'][0], self.log)

    def test_audit_log_displayed(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('logs', response.context)
        self.assertEqual(response.context['logs'][0], self.log)

    def test_redirect_if_not_team_leader(self):
        self.client.login(username=self.second_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/team_page/{self.team.team_id}/')


    
        