"""Tests of the edit_task view."""
from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from tasks.models import User, Task, Team, AuditLog
from tasks.forms import TaskForm

class EditTaskViewTestCase(TestCase):
    """Unit tests of the edit_task view."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username='@janedoe')

        self.form_input = {
            'title' : 'New task',
            'description' : 'This is a new task',
            'assigned_to' : [self.second_user.id],
            'due_date' : (datetime.now().date() + timedelta(days=2)),
            'priority' : 'high',
            'completed' : True
        }

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
            priority = 'low'
        )
        self.task.assigned_to.set([self.user])

        self.url = reverse('edit_task', kwargs={'task_id': self.task.id})

    def test_edit_task_url(self):
        self.assertEqual(self.url, f'/edit_task/{self.task.id}/')

    def test_get_edit_task(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_task.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TaskForm))
        self.assertFalse(form.is_bound)

    def test_get_edit_task_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_succesful_task_edit(self):
        self.client.login(username=self.user.username, password='Password123')
        self.team.team_members.add(self.second_user)
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_page', kwargs={'team_id': self.team.team_id}))
        task = Task.objects.get(id=self.task.id)
        self.assertEqual(task.title, self.form_input['title'])
        self.assertEqual(task.description, self.form_input['description'])
        self.assertEqual(task.due_date, self.form_input['due_date'])
        self.assertEqual(task.priority, self.form_input['priority'])
        self.assertEqual(task.assigned_to.count(), 1)
        self.assertIn(self.second_user, task.assigned_to.all())
        self.assertEqual(task.related_to_team, self.team)
        self.assertEqual(task.priority, self.form_input['priority'])
        self.assertEqual(task.completed, self.form_input['completed'])

    def test_unsuccesful_task_edit(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['assigned_to'] = []
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_task.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TaskForm))
        self.assertTrue(form.is_bound)
        task = Task.objects.get(id=self.task.id)
        self.assertEqual(task.title, self.task.title)
        self.assertEqual(task.description, self.task.description)
        self.assertEqual(task.due_date, self.task.due_date)
        self.assertEqual(task.priority, self.task.priority)
        self.assertEqual(task.completed, self.task.completed)

        self.assertEqual(task.assigned_to.count(), 1)
        self.assertIn(self.user, task.assigned_to.all())
        self.assertEqual(task.related_to_team, self.team)
        self.assertEqual(task.priority, self.task.priority)

    def test_only_creator_and_assigned_users_can_edit_tasks(self):
        self.client.login(username=self.second_user.username, password='Password123')
        self.team.team_members.add(self.second_user)
        response = self.client.get(self.url, follow = True)
        self.assertEqual(response.status_code, 200)
        response_url = reverse('team_page', kwargs={'team_id': self.team.team_id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_page.html')

    def test_edit_task_with_invalid_task_id(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(reverse('edit_task', kwargs={'task_id': 2}), follow = True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_audit_log_created(self):
        self.client.login(username=self.user.username, password='Password123')
        self.team.team_members.add(self.second_user)
        before_count = AuditLog.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = AuditLog.objects.count()
        self.assertEqual(after_count, before_count+1)
        log = AuditLog.objects.last()
        self.assertEqual(log.username, self.user)
        self.assertEqual(log.team, self.team)
        self.assertEqual(log.task_title, self.form_input['title'])
        self.assertEqual(log.action, 'edited')
        self.assertEqual(log.changes, 
           f"Title: {self.task.title} to {self.form_input['title']}\nDescription: {self.task.description} to {self.form_input['description']}"
           f"\nDue date: {self.task.due_date} to {self.form_input['due_date']}"
           f"\nPriority: low to high"     
           f"\nAssigned to: Added {self.second_user.username} Removed {self.user.username} "
           f"\nCompleted: False to True"         
        )