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
        self.url = reverse('add_members')
        
        self.form_input = {
            'usernames': '@janedoe'
        }

        self.team = Team.objects.create(
            team_name='Test team',
            team_description='This is a test team',
            team_leader=self.user
        )
        self.team.team_members.set([self.user])

    def test_add_members_url(self):
        self.assertEqual(self.url, '/add_members/')

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
        session = self.client.session
        session.update({'team': self.team.team_id})
        session.save()
        self.session = session
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Invites.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        invite = Invites.objects.get(username__username='@janedoe')
        self.assertEqual(invite.team_id, self.team.team_id)
        self.assertEqual(invite.invite_status, 'S')
    
    def test_unsuccesful_add_members(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['usernames'] = 'Not a user'
        before_count = Invites.objects.count()
        session = self.client.session
        session.update({'team': self.team.team_id})
        session.save()
        self.session = session
        response = self.client.post(self.url, self.form_input)
        after_count = Invites.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_members.html')
        form = response.context['form']


    