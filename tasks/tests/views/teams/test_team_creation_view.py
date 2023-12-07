"""Tests of the team_creation view."""

from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team
from tasks.forms import TeamCreationForm

class TeamCreationViewTestCase(TestCase):
    """Unit tests of the team_creation view."""

    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('team_creation')
        
        self.form_input = {
            'team_name': 'Test team',
            'team_description': 'This is a test team'
        }

    def test_team_creation_url(self):
        self.assertEqual(self.url, '/team_creation/')
    
    def test_get_team_creation(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team_creation.html')
        self.assertIsInstance(response.context['form'], TeamCreationForm)

    def test_get_team_creation_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_sucessful_team_creation(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Team.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count+1)
        team = Team.objects.get(team_name='Test team')
        response_url = reverse('add_members', kwargs={'team_id': team.team_id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'add_members.html')
        self.assertEqual(team.team_description, 'This is a test team')
        self.assertEqual(team.team_leader, self.user)
        self.assertEqual(team.team_members.first(), self.user)  

    def test_unsuccesful_team_creation(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['team_name'] = ''
        before_count = Team.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team_creation.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TeamCreationForm))
        self.assertTrue(form.is_bound)