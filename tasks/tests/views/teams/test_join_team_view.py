"""Tests of the join_team view."""

from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team, Invites
from tasks.forms import InviteForm

class JoinTeamViewTestCase(TestCase):
    """Unit tests of the join_team view."""

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

        self.url = reverse('join_team', kwargs={'team_id': self.team.team_id})

    def test_join_team_url(self):
        self.assertEqual(self.url, f'/join_team/{self.team.team_id}/')

    def test_join_team_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')    
    
    def test_join_team(self):
        self.client.login(username=self.second_user.username, password='Password123')
        before_count = Invites.objects.count()
        response = self.client.get(self.url, follow=True)
        after_count = Invites.objects.count()
        self.assertEqual(after_count, before_count-1)
        response_url = reverse('team_page', kwargs={'team_id': self.team.team_id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_page.html')
        self.assertIn(self.second_user, self.team.team_members.all())
        self.assertNotIn(self.invite, Invites.objects.all())

    def test_cannot_join_team_when_not_invited(self):
        self.invite.delete()
        self.client.login(username=self.second_user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertNotIn(self.second_user, self.team.team_members.all())
