from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import User, Team
from django.contrib.auth.models import User
from tasks.models import Team
from django.contrib.auth import get_user_model  
from tasks.models import User, Team


class TeamModelTestCase(TestCase):
    """Unit tests for the Team model."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username='@janedoe')
        self.team = Team.objects.create(
            team_leader=self.user, 
            team_name='Team Default', 
            team_description='Description for team'
        )
        self.team.team_members.set([self.user])

    def test_valid_team(self):
        self._assert_team_is_valid()

    def test_team_name_cannot_be_blank(self):
        self.team.team_name = '' 
        self._assert_team_is_invalid()

    def test_duplicate_team_name_allowed(self):
        duplicate_team = Team(
            team_leader=self.user,
            team_name='Team Default',
            team_description='Another team'
        )
        self.team.team_name = duplicate_team.team_name
        self._assert_team_is_valid()

    def test_team_name_may_contain_30_characters(self):
        self.team.team_name = 'x'*30 
        self._assert_team_is_valid()

    def test_team_name_must_not_contain_more_than_30_characters(self):
        self.team.team_name = 'x' + 'x'*30
        self._assert_team_is_invalid()

    def test_team_descriptions_can_be_same(self):
        duplicate_team = Team.objects.create(
            team_leader=self.user,
            team_name='Team A',
            team_description='Description'
        )
        self.team.team_description = duplicate_team.team_description
        self._assert_team_is_valid()
    
    def test_team_description_may_be_blank(self):
        self.team.team_description = ''
        self._assert_team_is_valid()

    def test_team_description_may_be_200_chars_long(self):
        self.team.team_description = 'x'*200
        self._assert_team_is_valid()
    
    def test_team_description_may_not_exceed_200_chars(self):
        self.team.team_description = 'x' + 'x'*200
        self._assert_team_is_invalid()   

    def test_team_members_can_be_added(self):
        self.team.team_members.add(self.second_user)
        self._assert_team_is_valid()     

    def test_team_leader_must_exist(self):
        self.team.team_leader = None
        self._assert_team_is_invalid()

    def test_team_name_unique_to_team_leader(self):
        # Create a team with a unique team name for the team leader
        unique_team = Team(
            team_leader=self.user,
            team_name='Unique Team',
            team_description='Unique Description'
        )
        self.team.team_name = unique_team.team_name
        self._assert_team_is_valid()

    def test_team_members_must_exist(self):
        # Try to add a non-existent user as a team member
        self.team.team_members.add(None)
        self._assert_team_is_valid()
    
    def test_team_member_uniqueness(self):
        # Ensure the same team member is not added twice
        team_member = get_user_model().objects.get(username="@johndoe")
        self.team.team_members.add(team_member)
        self.team.team_members.add(team_member)
        self._assert_team_is_valid()

    def test_team_member_can_be_removed(self):
        # Add a team member and then remove
        team_member = get_user_model().objects.get(username="@johndoe")
        self.team.team_members.add(team_member)
        self.team.team_members.remove(team_member)
        self._assert_team_is_valid()

    def test_team_name_may_not_be_unique(self):
        # Create another team with the same name and different leader
        another_user = get_user_model().objects.get(username="@johndoe")
        duplicate_team = Team(
            team_leader=another_user,
            team_name='Team Default',
            team_description='Another team'
        )
        self._assert_team_is_valid()

    def test_team_member_count(self):
        # Add three team members
        team_members = get_user_model().objects.filter(username__in=["@johndoe", "@janedoe"])
        self.team.team_members.set(team_members)
        self.assertEqual(self.team.team_members.count(), 2) 

    def _assert_team_is_valid(self):
        try:
            self.team.full_clean()
        except (ValidationError):
            self.fail('Test team should be valid')

    def _assert_team_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.team.full_clean()
    
    
    
