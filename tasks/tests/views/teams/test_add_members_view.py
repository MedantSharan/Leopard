"""Tests of the add_members view."""

from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team, Invites
from tasks.forms import InviteForm

class AddMembersViewTestCase(TestCase):
    """Unit tests of the add_members view."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        
        self.form_input = {
            'usernames': '@janedoe'
        }

        self.team = Team.objects.create(
            team_name='Test team',
            team_description='This is a test team',
            team_leader=self.user
        )
        self.team.team_members.set([self.user])

        self.url = reverse('add_members', kwargs={'team_id': self.team.team_id})

    def test_add_members_url(self):
        self.assertEqual(self.url, f'/add_members/{self.team.team_id}/')

    def test_get_add_members(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_members.html')
        self.assertIsInstance(response.context['form'], InviteForm)

    def test_get_add_members_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_sucessful_add_members(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Invites.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Invites.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('team_page', kwargs={'team_id': self.team.team_id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_page.html')
        invite = Invites.objects.get(username__username='@janedoe')
        self.assertEqual(invite.team_id, self.team.team_id)
    
    def test_unsuccesful_add_members(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['usernames'] = 'Not a user'
        before_count = Invites.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Invites.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_members.html')
        form = response.context['form']


    