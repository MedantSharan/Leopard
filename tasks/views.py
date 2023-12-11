from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm,TeamCreationForm, InviteForm, TaskForm
from tasks.helpers import login_prohibited
from .models import Invites,Team, Task, User, AuditLog
from django.db.models import Q
from django.template.defaulttags import register
import copy

@login_required
def remove_member(request, team_id, username):
    """Allows Team Members to leave current team"""
    user = User.objects.get(username = username)
    if Team.objects.filter(team_id = team_id).exists():
        team = Team.objects.get(team_id = team_id)
    else:
        return redirect('dashboard')
    team_member = team.team_members.filter(username = username)
    tasks = Task.objects.filter(related_to_team = team, assigned_to = user)
    if team_member and user != team.team_leader and request.user == team.team_leader:
        team.team_members.remove(user)
        if tasks:
            for task in tasks:
                task.assigned_to.remove(user)
                if task.assigned_to.count() == 0:
                    # If last member assigned to task is removed, delete task
                    task.delete()
        return redirect('team_page', team_id = team_id)
    else:
        return redirect('dashboard')

@login_required
def leave_team(request, team_id):
    """Allows Team Members to leave current team"""
    if Team.objects.filter(team_id = team_id).exists():
        team = Team.objects.get(team_id = team_id)
    else:
        return redirect('dashboard')
    if request.user != team.team_leader and request.user in team.team_members.all():
        tasks = Task.objects.filter(related_to_team = team, assigned_to = request.user)
        team.team_members.remove(request.user)
        if tasks:
            for task in tasks:
                task.assigned_to.remove(request.user)
                if task.assigned_to.count() == 0:
                    # If last member assigned to task leaves, delete task
                    task.delete()
        return redirect('dashboard')
    else:
        return redirect('dashboard')


@login_required
def delete_team(request, team_id):
    """Allow Team Leader to delete current team"""
    team = Team.objects.filter(team_id = team_id ,team_leader = request.user)
    team_task = Team.objects.get(team_id = team_id)
    for invite in Invites.objects.filter(team_id=team_id):
        invite.delete()
    if team:
        team.delete()
    return redirect('dashboard')

@login_required
def decline_team(request, team_id):
    """Allows users to decline invites to teams"""
    invite = Invites.objects.filter(team_id = team_id ,username = request.user)
    if invite:
        invite.delete()
    return redirect('dashboard')

@login_required
def join_team(request, team_id):
    """Allows users to accept invites to teams"""
    invite = Invites.objects.filter(team_id = team_id ,username = request.user)
    if invite:
        invite.delete()
        team = Team.objects.get(team_id = team_id)
        team.team_members.add(request.user)
        return redirect('team_page', team_id = team_id)
    else:
        return redirect('dashboard')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@login_required
def team_page(request, team_id):
    """Displays selected team page information"""
    if Team.objects.filter(team_id=team_id).exists():
        teams = Team.objects.get(team_id=team_id)
        tasks_from_team = Task.objects.filter(related_to_team = teams)
        user = request.user
        teams_members = []
        for member in teams.team_members.all():
            teams_members.append(member)

        tasks_assigned = request.GET.get('assigned_to')
        tasks_from_team = get_filtered_tasks(request, tasks_assigned, team_id)

        return render(request, 'team_page.html', {'teams' : teams, 'tasks' : tasks_from_team, 'user': user, 'teams_members': teams_members})
    else:
        return redirect('dashboard')

@login_required
def dashboard(request):
    """Display the current user's dashboard."""
    current_user = request.user
    invite_list = []
    team_names = {}
    user_teams = Team.objects.filter(team_members__in=[current_user])
    teams = Team.objects.filter(team_id__in=user_teams.values('team_id'))
    tasks = Task.objects.filter(assigned_to__in=[current_user])

    for invite in Invites.objects.filter(username=current_user):
        invite_list.append(invite)

    for invite in invite_list:
        team_names[invite.team_id] = (Team.objects.get(team_id = invite.team_id)).team_name

    tasks = get_filtered_tasks(request) # Filter tasks if search query is provided

    return render(request, 'dashboard.html', {'user': current_user, 'team_invites': team_names, 'invites': invite_list, 'teams' : teams, 'tasks' : tasks})

@login_required
def add_members(request, team_id):
    """Display form that allows team leaders to add Members to their team"""
    if request.method == 'POST':
        form = InviteForm(request.POST, team_id=team_id) 
        if form.is_valid():
            form.save()
            return redirect('team_page', team_id = team_id) 
    else:
        form = InviteForm()
    return render(request, "add_members.html", {'form': form, 'team_id': team_id})

@login_required
def team_creation(request):
    """Displays form to create a team with current user as leader"""
    if request.method == 'POST':
        form = TeamCreationForm(request.POST, request.FILES) 
        if form.is_valid():
            team = form.save(commit=False)
            team.team_leader = request.user
            team.save()
            team.team_members.set([request.user])
            team.save
            return redirect('add_members', team_id = team.team_id); 
    else:
        form = TeamCreationForm()
    return render(request, "team_creation.html", {'form': form})


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

@login_required
def requests_table(request):
     invites = get_invites()
     return render(request, 'dashboard_html', {'invites': invites})

# def fake_dashboard(request):
#     fake_invite = Invite(sender='TestSender', message='TestMessage')
#     invites = [fake_invite]
#     return render(request, 'dashboard.html', {'invites': invites})

class LoginProhibitedMixin: 
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

@login_required
def create_task(request, team_id):
    """Handle displaying and processing the task creation form."""

    if not Team.objects.filter(team_id = team_id).exists():
        return redirect('dashboard')
    if request.method == 'POST':
        form = TaskForm(team_id, request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit = False)
            task.created_by = request.user
            assigned_to_user = form.cleaned_data.get('assigned_to')
            task.related_to_team = Team.objects.get(team_id = team_id)
            task.save()
            task.assigned_to.set(assigned_to_user)
            task.save()
            audit_log_add(request, team_id, task.title, request.user, 'created')
            return redirect('team_page', team_id = team_id)
    else: 
        form = TaskForm(team_id)
    return render(request, 'task.html', {'form' : form, 'team_id' : team_id})

@login_required
def edit_task(request, task_id):
    """Display the task edit page and handle task edits."""

    if not Task.objects.filter(pk = task_id).exists():
        return redirect('dashboard')
    task = Task.objects.get(pk = task_id)
    team_id = task.related_to_team.team_id
    if(request.user == task.created_by or request.user in task.assigned_to.all()):
        if request.method == 'POST':
            before_edit = copy.deepcopy(task)
            before_assigned_to = set(task.assigned_to.all())
            form = TaskForm(team_id, request.POST, request.FILES, instance = task)
            if form.is_valid():
                form.save()
                after_edit = form.instance
                changes = compare_task_details(before_edit, after_edit, before_assigned_to)
                audit_log_add(request, team_id, task.title, request.user, 'edited', changes)
                return redirect('team_page', team_id = team_id)
        else: 
            form = TaskForm(team_id, instance = task)
        return render(request, 'edit_task.html', {'form' : form})
    else:
        return redirect('team_page', team_id = team_id)

@login_required
def delete_task(request, task_id):
    """Handle deletion of tasks."""

    if not Task.objects.filter(pk = task_id).exists():
        return redirect('dashboard')
    task = Task.objects.get(pk = task_id)
    team_id = task.related_to_team.team_id
    if(request.user == task.created_by):
        audit_log_add(request, team_id, task.title, request.user, 'deleted')
        task.delete()
    return redirect('team_page', team_id = team_id)


@login_required
def view_task(request, task_id):
    """Display the task view page."""

    if not Task.objects.filter(pk = task_id).exists():
        return redirect('dashboard')
    task = Task.objects.get(pk = task_id)
    return render(request, 'view_task.html', {'task' : task})

@login_required
def task_search(request):
    """Display the task search page and filter tasks by search."""
    
    user_teams = Team.objects.filter(team_members__in=[request.user])
    tasks = get_filtered_tasks(request) # Filter tasks if search query is provided

    return render(request, 'task_search.html', {'tasks': tasks, 'teams' : user_teams})

def get_filtered_tasks(request, assigned_to = None, team_id = None):
    """Return a list of filtered tasks based on search and order_by."""

    query = request.GET.get('q', '')
    order_by = request.GET.get('order_by', 'due_date')
    teams_search = request.GET.get('team', '')

    if team_id:
        # Allow for filtering by team if team_id is provided
        tasks = Task.objects.filter(related_to_team__team_id=team_id)
    else:
        # Otherwise, filter by tasks assigned to the current user
        tasks = Task.objects.filter(assigned_to__in=[request.user])

    if query:
        # Filter by search query if provided
        tasks = tasks.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if teams_search:
        selected_team = Team.objects.get(team_id=teams_search)
        tasks = tasks.filter(related_to_team=selected_team)

    if assigned_to:
        tasks = tasks.filter(assigned_to__username=assigned_to)
    
    # Custom priority order
    custom_priority_order = {'': 3, 'low': 2, 'medium': 1, 'high': 0}

    if order_by == 'priority':
        # Order tasks using custom priority key
        tasks = sorted(tasks, key=lambda task: custom_priority_order.get(task.priority, 0))
    elif order_by == 'due_date':
        tasks = tasks.order_by('due_date')
    elif order_by == 'title':
        tasks = tasks.order_by('title')

    return tasks

@login_required
def audit_log(request, team_id):
    """Display the audit log page."""
    team = Team.objects.get(team_id = team_id)

    if not request.user == team.team_leader:
        return redirect('team_page', team_id = team_id)
    else:
        logs = AuditLog.objects.filter(team_id = team_id)
        return render(request, 'audit_log.html', {'logs' : logs})

def audit_log_add(request, team_id, task, username, action, changes = None):
    """Add an audit log entry."""

    team = Team.objects.get(team_id = team_id)

    if(AuditLog.objects.filter(team_id = team_id).count() >= 20 and changes):
        # If there are more than 20 logs, delete the oldest one
        AuditLog.objects.filter(team_id = team_id).order_by('timestamp').first().delete()

    if action == 'edited' and not changes:
        return

    AuditLog.objects.create(
        username = username, 
        team = team,
        task_title = task, 
        action = action,
        changes = changes
    )

def compare_task_details(before_edit, after_edit, assigned):
    """Find changes made during task edits."""

    changes = []
    for field, display_name in [('title', 'Title'), ('description', 'Description'), ('due_date', 'Due date'), ('priority', 'Priority'), ('assigned_to', 'Assigned to')]:
        value_before = getattr(before_edit, field)
        value_after = getattr(after_edit, field)

        if field == 'assigned_to':
            before_users = set(assigned)
            after_users = set(value_after.all())

            added_users = after_users - before_users
            removed_users = before_users - after_users
            if not before_users == after_users:
                if added_users:
                    added_usernames = ', '.join(user.username for user in added_users)
                    changes.append(f"{display_name}: Added {added_usernames}")

                if removed_users:
                    removed_usernames = ', '.join(user.username for user in removed_users)
                    changes.append(f"{display_name}: Removed {removed_usernames}")
                continue

        if value_before != value_after:
            change_string = f"{display_name}: '{value_before}' to '{value_after}'"
            changes.append(change_string)

    return '\n'.join(changes)