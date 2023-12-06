"""Tests of the remove_member view."""

from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team, Invites, Task
from tasks.forms import InviteForm

class RemoveMemberViewTestCase(TestCase):
    """Unit tests of the remove_member view."""

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
        self.team.team_members.set([self.user, self.second_user])

        self.invite = Invites.objects.create(
            username=self.second_user,
            team_id=self.team.team_id,
            invite_status='S'
        )

        self.task = Task.objects.create(title = 'Test task',
            description = 'This is a test task',
            created_by = self.second_user,
            related_to_team = self.team,
        )
        self.task.assigned_to.set([self.second_user])

        self.url = reverse('remove_member', kwargs={'team_id': self.team.team_id, 'username': self.second_user.username})

    def test_remove_member_url(self):
        self.assertEqual(self.url, f'/remove_member/{self.team.team_id}/{self.second_user.username}/')

    def test_remove_member_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_remove_member(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = self.team.team_members.count()
        response = self.client.get(self.url, follow=True)
        after_count = self.team.team_members.count()
        self.assertEqual(after_count, before_count-1)
        response_url = reverse('team_page', kwargs={'team_id': self.team.team_id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_page.html')
        self.assertNotIn(self.second_user, self.team.team_members.all())

    def test_cannot_remove_team_leader(self):
        self.team.team_leader = self.second_user
        self.client.login(username=self.second_user.username, password='Password123')
        before_count = self.team.team_members.count()
        response = self.client.get(self.url, follow=True)
        after_count = self.team.team_members.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn(self.user, self.team.team_members.all())

    def test_cannot_remove_team_member_when_not_team_leader(self):
        self.client.login(username=self.second_user.username, password='Password123')
        self.url = reverse('remove_member', kwargs={'team_id': self.team.team_id, 'username': self.user.username})
        before_count = self.team.team_members.count()
        response = self.client.get(self.url, follow=True)
        after_count = self.team.team_members.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn(self.second_user, self.team.team_members.all())

    def test_cannot_remove_team_member_when_not_team_member(self):
        self.client.login(username=self.second_user.username, password='Password123')
        self.team.team_members.remove(self.second_user)
        self.url = reverse('remove_member', kwargs={'team_id': self.team.team_id, 'username': self.user.username})
        before_count = self.team.team_members.count()
        response = self.client.get(self.url, follow=True)
        after_count = self.team.team_members.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_tasks_deleted_if_last_assigned_user_removed(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Task.objects.count()
        response = self.client.get(self.url, follow=True)
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count-1)
        response_url = reverse('team_page', kwargs={'team_id': self.team.team_id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_page.html')
        self.assertNotIn(self.task, Task.objects.all())
        self.assertNotIn(self.task, self.second_user.assigned_tasks.all())
