"""Tests of the edit_task view."""
from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from tasks.models import User, Task, Team
from tasks.forms import TaskForm

class EditTaskViewTestCase(TestCase):
    """Unit tests of the edit_task view."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')

        self.form_input = {
            'title' : 'New task',
            'description' : 'This is a new task',
            'assigned_to' : [self.user.id],
            'due_date' : (datetime.now().date() + timedelta(days=2)),
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
        )
        self.task.assigned_to.set([self.user])
        self.task.related_to_team = self.team
        self.task.save()

        self.url = reverse('edit_task', kwargs={'task_id': self.task.id})

    def test_edit_task_url(self):
        self.assertEqual(self.url, f'/edit_task/{self.task.id}')

    def test_get_edit_task(self):
        self.client.login(username=self.user.username, password='Password123')
        session = self.client.session
        session.update({'team': self.team.team_id})
        session.save()
        self.session = session
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
        session = self.client.session
        session.update({'team': self.team.team_id})
        session.save()
        self.session = session
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_page', kwargs={'team_id': self.team.team_id}))
        task = Task.objects.get(id=self.task.id)
        self.assertEqual(task.title, self.form_input['title'])
        self.assertEqual(task.description, self.form_input['description'])
        self.assertEqual(task.due_date, self.form_input['due_date'])
        self.assertEqual(task.assigned_to.count(), 1)
        self.assertEqual(task.assigned_to.first().username, self.user.username)
        self.assertEqual(task.related_to_team, self.team)

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
        self.assertEqual(task.assigned_to.count(), 1)
        self.assertEqual(task.assigned_to.first().username, self.user.username)
        self.assertEqual(task.related_to_team, self.team)