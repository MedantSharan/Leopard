"""Unit tests of the team creation form."""
from django import forms
from django.test import TestCase
from tasks.forms import TeamCreationForm
from tasks.models import User, Team
from django.urls import reverse

class TeamCreationTestCase(TestCase):
    """Unit tests of the team creation form."""

    fixtures = ['tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/other_users.json']

    def setUp(self):
        self.userJohn= User.objects.get(username="@johndoe")
        self.userJane = User.objects.get(username="@janedoe")
        self.userPetra = User.objects.get(username="@petrapickles")
        self.form_input = {
            'team_name' : 'Test Team',
            'team_description' : 'A test team description',
        }


    def test_form_contains_required_fields(self):
        form = TeamCreationForm()
        self.assertIn('team_name', form.fields)
        self.assertIn('team_description', form.fields)

    def test_form_accepts_valid_input(self):
        form = TeamCreationForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_team_name(self):
        self.form_input['team_name'] = ''
        form = TeamCreationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_blank_description(self):
        self.form_input['team_description'] = ''
        form = TeamCreationForm(data=self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_form_rejects_invalid_task_name(self):
        self.form_input['team_name'] = 'a'*31
        form = TeamCreationForm(data=self.form_input)
        self.assertFalse(form.is_valid())


    def test_team_creation_form_must_save_correctly(self):
        form = TeamCreationForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        
        before_count = Team.objects.count()
        team = form.save(commit=False)
        team.team_leader = self.userJohn
        team.team_id = 1
        team.save()
        after_count = Team.objects.count()

        self.assertEqual(after_count, before_count + 1)

        saved_team = Team.objects.get(team_name='Test Team')
        self.assertEqual(saved_team.team_name, 'Test Team')
        self.assertEqual(saved_team.team_description, 'A test team description')
        self.assertEqual(saved_team.team_leader, self.userJohn)
        self.assertEqual(saved_team.team_id, 1)
   
