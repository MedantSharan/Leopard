from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from tasks.models import Invites, Team

class InvitesModelTestCase(TestCase):
    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.team_leader = get_user_model().objects.get(username="@johndoe")
        self.team_member = get_user_model().objects.get(username="@janedoe")
        self.team = Team.objects.create(
            team_leader=self.team_leader,
            team_name='Team Default',
            team_description='Description for team'
        )
        self.invite = Invites(username=self.team_member, team_id=self.team.team_id)

    def test_valid_invite(self):
        self._assert_invite_is_valid()

    def test_duplicate_invite_not_allowed(self):
        # Create a duplicate invite
        duplicate_invite = Invites(username=self.team_member, team_id=self.team.team_id)
        self._assert_invite_is_valid()


    def test_team_member_can_send_invite(self):
        # Ensure team member can send an invite
        team_member_sender = Invites(username=self.team_member, team_id=self.team.team_id)
        self._assert_invite_is_valid()

    def test_validity_of_team_id(self):
        # Ensure invite with an invalid team_id is invalid
        invalid_team_id_invite = Invites(username=self.team_member, team_id=999)
        self._assert_invite_is_valid()

    def _assert_invite_is_valid(self):
        try:
            self.invite.full_clean()
        except ValidationError:
            self.fail('Test invite should be valid')

    def _assert_invite_is_invalid(self, invite=None):
        if invite is None:
            invite = self.invite

        with self.assertRaises(ValidationError):
            invite.full_clean()
    
    def test_for_duplicates(self):
        # Create a duplicate invite
        duplicate_invite = Invites(username=self.team_member, team_id=self.team.team_id)
        self._assert_invite_is_valid()

    def test_every_team_member_can_send_invite(self):
        # Ensure team member can send an invite
        team_member_sender = Invites(username=self.team_member, team_id=self.team.team_id)
        self._assert_invite_is_valid()

    def test_team_id_validity(self):
        # Ensure invite with an invalid team_id is invalid
        invalid_team_id_invite = Invites(username=self.team_member, team_id=999)
        self._assert_invite_is_valid()

    def test_empty_username_not_allowed(self):
        # Ensure invite with an empty username is invalid
        empty_username_invite = Invites(username=None, team_id=self.team.team_id)
        self._assert_invite_is_invalid(empty_username_invite)

    def test_team_member_validity(self):
        # Ensure invite with a non-existent team member is invalid
        invalid_team_member_invite = Invites(username=get_user_model().objects.create(username="nonexistent"), team_id=self.team.team_id)
        self._assert_invite_is_valid()

    def test_team_id_range(self):
        # Ensure an invite is pending by default
        invite = Invites.objects.create(username=self.team_member, team_id=2000)
        self._assert_invite_is_valid()

    def test_team_member_can_have_multiple_invites(self):
        # Ensure a team member can have multiple invites from different teams
        Invites.objects.create(username=self.team_member, team_id=1)
        Invites.objects.create(username=self.team_member, team_id=2)
        self.assertEqual(Invites.objects.filter(username=self.team_member).count(), 2)

    def test_team_member_can_not_only_have_one_invite_per_team(self):
        # Ensure a team member can have duplicate invites
        Invites.objects.create(username=self.team_member, team_id=1)
        duplicate_invite = Invites(username=self.team_member, team_id=1)
        self._assert_invite_is_invalid(duplicate_invite)