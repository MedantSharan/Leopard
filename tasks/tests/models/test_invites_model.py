from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from tasks.models import Invites, Team, User

class InvitesModelTestCase(TestCase):
    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.team_leader = User.objects.get(username="@johndoe")
        self.team_member = User.objects.get(username="@janedoe")
        self.team = Team.objects.create(
            team_leader=self.team_leader,
            team_name='Team Default',
            team_description='Description for team'
        )
        self.invite = Invites.objects.create(username=self.team_member, team_id=self.team.team_id)

    def test_valid_invite(self):
        self._assert_invite_is_valid()

    def test_duplicate_invite_not_allowed(self):
        with self.assertRaises(IntegrityError):
            Invites.objects.create(username=self.team_member, team_id=self.team.team_id)

    def _assert_invite_is_valid(self):
        try:
            self.invite.full_clean()
        except ValidationError:
            self.fail('Test invite should be valid')

    def _assert_invite_is_invalid(self):
        if invite is None:
            invite = self.invite

        with self.assertRaises(ValidationError):
            invite.full_clean()

    def test_empty_username_not_allowed(self):
        with self.assertRaises(IntegrityError):
            empty_username_invite = Invites.objects.create(username=None, team_id=self.team.team_id)

    def test_team_member_can_have_multiple_invites(self):
        Invites.objects.create(username=self.team_member, team_id=2)
        self.assertEqual(Invites.objects.filter(username=self.team_member).count(), 2)

    def test_team_member_can_only_have_one_invite_per_team(self):
        with self.assertRaises(IntegrityError):
            Invites.objects.create(username=self.team_member, team_id=self.team.team_id)