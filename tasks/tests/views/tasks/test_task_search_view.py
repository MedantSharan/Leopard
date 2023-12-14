"""Tests of the task_search view."""
from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from tasks.models import User, Task, Team
from tasks.forms import TaskForm

class TaskSearchViewTestCase(TestCase):
    """Unit tests of the task_search view."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')

        self.team = Team.objects.create(team_id = 1, 
            team_leader = self.user, 
            team_name ='Test team', 
            team_description = 'This is a test team'
        )
        self.team.team_members.set([self.user])

        self.task = Task.objects.create(title = 'Test task',
            description = 'This is a test task',
            created_by = self.user,
            due_date = (datetime.now().date() + timedelta(days=1)),
            related_to_team = self.team,
            priority = 'low',
        )
        self.task.assigned_to.set([self.user])

        self.url = reverse('task_search')

    def test_task_search_url(self):
        self.assertEqual(self.url, '/task_search/')

    def test_get_task_search(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_search.html')
    
    def test_get_task_search_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_task_search_with_team(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'team': self.team.team_id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_search.html')
        self.assertContains(response, 'Test task')

    def test_task_search_without_team(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_search.html')
        self.assertContains(response, 'Test task')

    def test_task_search_with_query(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'q': 'Test task'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_search.html')
        self.assertContains(response, 'Test task')

    def test_task_search_with_no_results(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'q': 'Not a task'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_search.html')
        self.assertNotContains(response, 'Test task')

    def test_team_filter(self):
        self.client.login(username=self.user.username, password='Password123')
        new_team = Team.objects.create(
            team_leader = self.user, 
            team_name ='New team', 
            team_description = 'This is a new test team'
        )
        new_team.team_members.set([self.user])
        new_task = Task.objects.create(
            title = 'New task',
            description = 'This is a new test task',
            created_by = self.user,
            related_to_team = new_team,
        )
        new_task.assigned_to.set([self.user])

        response = self.client.get(self.url, {'team': self.team.team_id}, follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_search.html')
        self.assertContains(response, 'Test task')
        self.assertNotContains(response, 'New task')

    def test_order_by_title(self):
        self.client.login(username=self.user.username, password='Password123')
        new_task = Task.objects.create(
            title = 'New task',
            description = 'This is a new test task',
            created_by = self.user,
            related_to_team = self.team,
        )
        new_task.assigned_to.set([self.user])

        response = self.client.get(self.url, {'order_by': 'title'}, follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_search.html')
        self.assertContains(response, 'New task')
        self.assertContains(response, 'Test task')
        content = response.content.decode('utf-8')
        index_test_task = content.find('Test task')
        index_new_task = content.find('New task')
        self.assertLess(index_new_task, index_test_task)

    def test_order_by_priority(self):
        self.client.login(username=self.user.username, password='Password123')
        new_task = Task.objects.create(
            title = 'New task',
            description = 'This is a new test task',
            created_by = self.user,
            related_to_team = self.team,
            priority = 'high',
        )
        new_task.assigned_to.set([self.user])

        response = self.client.get(self.url, {'order_by': 'priority'}, follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_search.html')
        self.assertContains(response, 'New task')
        self.assertContains(response, 'Test task')
        content = response.content.decode('utf-8')
        index_test_task = content.find('Test task')
        index_new_task = content.find('New task')
        self.assertLess(index_new_task, index_test_task)

    def test_order_by_completion(self):
        self.client.login(username=self.user.username, password='Password123')
        new_task = Task.objects.create(
            title = 'New task',
            description = 'This is a new test task',
            created_by = self.user,
            related_to_team = self.team,
            priority = 'high',
            completed = True,
        )
        new_task.assigned_to.set([self.user])

        response = self.client.get(self.url, {'order_by': 'completion'}, follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_search.html')
        self.assertContains(response, 'New task')
        self.assertContains(response, 'Test task')
        content = response.content.decode('utf-8')
        index_test_task = content.find('Test task')
        index_new_task = content.find('New task')
        self.assertLess(index_test_task, index_new_task)

