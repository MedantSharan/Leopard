"""Tests of the delete_team view."""

from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team, Invites, Task
from tasks.forms import InviteForm

class DeleteTeamViewTestCase(TestCase):
    """Unit tests of the delete_team view."""

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

        self.invite = Invites.objects.create(
            username=self.second_user,
            team_id=self.team.team_id,
            invite_status='S'
        )

        self.task = Task.objects.create(title = 'Test task',
            description = 'This is a test task',
            created_by = self.user,
            related_to_team = self.team,
        )
        self.task.assigned_to.set([self.user])

        self.url = reverse('delete_team', kwargs={'team_id': self.team.team_id})

    def test_delete_team_url(self):
        self.assertEqual(self.url, f'/delete_team/{self.team.team_id}/')

    def test_delete_team_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_delete_team(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Team.objects.count()
        response = self.client.get(self.url, follow=True)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count-1)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertNotIn(self.team, Team.objects.all())
        self.assertNotIn(self.team, self.user.member_of_team.all())
        self.assertNotIn(self.team, self.second_user.member_of_team.all())
        self.assertNotIn(self.invite, Invites.objects.all())
        self.assertNotIn(self.task, Task.objects.all())
        
    def test_cannot_delete_team_when_not_team_member(self):
        self.client.login(username=self.second_user.username, password='Password123')
        before_count = Team.objects.count()
        response = self.client.get(self.url, follow=True)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_cannot_delete_team_when_not_team_leader(self):
        self.team.team_members.add(self.second_user)
        self.client.login(username=self.second_user.username, password='Password123')
        before_count = Team.objects.count()
        response = self.client.get(self.url, follow=True)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')