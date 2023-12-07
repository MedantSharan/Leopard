"""Tests of the create_task view."""
from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from tasks.models import User, Task, Team
from tasks.forms import TaskForm

class CreateTaskViewTestCase(TestCase):
    """Unit tests of the create_task view."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.form_input = {
            'title' : 'Test task',
            'description' : 'This is a test task',
            'assigned_to' : [self.user.id],
            'due_date' : (datetime.now().date() + timedelta(days=1)),
        }

        self.team = Team.objects.create(team_id = 1, 
            team_leader = self.user, 
            team_name ='Test team', 
            team_description = 'This is a test team'
        )
        self.team.team_members.set([self.user])
        
        self.url = reverse('create_task', kwargs={'team_id': self.team.team_id})
    
    def test_create_task_url(self):
        self.assertEqual(self.url, f'/create_task/{self.team.team_id}/')

    def test_get_create_task(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TaskForm))
        self.assertFalse(form.is_bound)

    def test_get_create_task_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_unsuccesful_task_creation(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['assigned_to'] = []
        before_count = Task.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TaskForm))
        self.assertTrue(form.is_bound)

    def test_succesful_task_creation(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Task.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('team_page', kwargs={'team_id': self.team.team_id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_page.html')
        task = Task.objects.get(title = 'Test task')
        self.assertEqual(task.title, 'Test task')
        self.assertEqual(task.description, 'This is a test task')
        self.assertEqual(task.assigned_to.first(), self.user)
        self.assertEqual(task.due_date, (datetime.now().date() + timedelta(days = 1)))
        self.assertEqual(task.related_to_team, self.team)

    def test_post_create_task_redirects_when_not_logged_in(self):
        before_count = Task.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_create_task_with_invalid_team(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(reverse('create_task', kwargs={'team_id': 2}), follow = True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
