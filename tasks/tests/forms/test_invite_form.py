"""Unit tests of the invite form."""
from django import forms
from django.test import TestCase
from tasks.forms import InviteForm
from tasks.models import User,Team, Invites

class InviteFormTestCase(TestCase):
    """Unit tests of the invite form."""

    fixtures = ['tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/other_users.json',]

    def setUp(self):
        self.userJohn= User.objects.get(username="@johndoe")
        self.userJane = User.objects.get(username="@janedoe")
        self.userPetra = User.objects.get(username="@petrapickles")

        self.team = Team.objects.create(
            team_id=1,
            team_leader=self.userJohn,
            team_name="Test Team",
            team_description = 'This is a test team')
        self.team.team_members.set([self.userJohn, self.userPetra])
        self.form_input = {'usernames': "@janedoe"}

    def test_form_contains_required_fields(self):
        form = InviteForm()
        self.assertIn('usernames', form.fields)

    def test_form_accepts_valid_input(self):
        form = InviteForm(data=self.form_input, team_id=self.team.team_id)
        self.assertTrue(form.is_valid())

    def test_form_rejects_invalid_username(self):
        self.form_input['usernames'] = 'johndoe'
        form = InviteForm(data=self.form_input,team_id=self.team.team_id)
        self.assertFalse(form.is_valid())

    def test_form_rejects_user_that_doesnt_exist(self):
        self.form_input['usernames'] = '@petercrouchdoesntexist'
        form = InviteForm(data=self.form_input,team_id=self.team.team_id)
        self.assertFalse(form.is_valid())

    def test_form_rejects_user_already_on_the_team(self):
        self.form_input['usernames'] = '@petrapickles'
        form = InviteForm(data=self.form_input, team_id=self.team.team_id)
        self.assertFalse(form.is_valid())


    def test_form_rejects_user_that_is_leader(self):
        self.form_input['usernames'] = '@johndoe'
        form = InviteForm(data=self.form_input, team_id=self.team.team_id)
        self.assertFalse(form.is_valid())

    def test_form_accpets_duplicates_of_existing_user_as_one_entry(self):
        self.form_input['usernames'] = '@janedoe, @janedoe, @janedoe, @janedoe, @janedoe'
        form = InviteForm(data=self.form_input, team_id=self.team.team_id)
        self.assertTrue(form.is_valid())

    def test_form_must_save_correctly(self):
        form = InviteForm(data=self.form_input, team_id=self.team.team_id)
        before_count = Invites.objects.count()
        form.save()
        after_count = Invites.objects.count()
        self.assertEqual(after_count, before_count+1)
        invite = Invites.objects.get(username=self.userJane, team_id=self.team.team_id)
        self.assertEqual(invite.username.username, "@janedoe")
        self.assertEqual(invite.team_id, 1)

    def test_form_must_add_errors_correctly(self):
        self.form_input['usernames'] = '@johndoe'
        form = InviteForm(data=self.form_input, team_id=self.team.team_id)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['usernames'][0], "User '@johndoe' is already in this team")