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
from .models import Invites,Team, Task, User
from django.template.defaulttags import register


def remove_member(request, team_id, username):
    """Allows Team Members to leave current team"""
    user = User.objects.get(username = username)
    team = Team.objects.get(team_id = team_id)
    team_member = Team.objects.filter(team_members=user)
    tasks = Task.objects.filter(related_to_team = team, assigned_to = user)
    if team_member:
        team.team_members.remove(user)
    if tasks:
        for task in tasks:
            task.assigned_to.remove(user)
            if task.assigned_to.count() == 0:
                task.delete()
    return redirect('dashboard')

def leave_team(request, team_id):
    """Allows Team Members to leave current team"""
    team = Team.objects.get(team_id = team_id)
    tasks = Task.objects.filter(related_to_team = team, assigned_to = request.user)
    if team:
        team.team_members.remove(request.user)
    if tasks:
        for task in tasks:
            task.assigned_to.remove(request.user)
            if task.assigned_to.count() == 0:
                task.delete()
    return redirect('dashboard')

def delete_team(request, team_id):
    """Allow Team Leader to delete current team"""
    team = Team.objects.filter(team_id = team_id ,team_leader = request.user)
    team_task = Team.objects.get(team_id = team_id)
    for invite in Invites.objects.filter(team_id=team_id):
        invite.delete()
    if team:
        team.delete()
    return redirect('dashboard')

def decline_team(request, team_id):
    invite = Invites.objects.filter(team_id = team_id ,username = request.user)
    if invite:
        invite.delete()
    return redirect(reverse('dashboard'))


def join_team(request, team_id):
    invite = Invites.objects.filter(team_id = team_id ,username = request.user)
    if invite:
        invite.delete()
        team = Team.objects.get(team_id = team_id)
        team.team_members.add(request.user)
    return redirect(reverse('team_page', kwargs = {'team_id' : team_id}))

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def team_page(request, team_id):
    teams = Team.objects.get(team_id=team_id)
    tasks_from_team = Task.objects.filter(related_to_team = teams)
    request.session['team'] = team_id
    user = request.user
    teams_members = []
    for member in teams.team_members.all():
        teams_members.append(member)
    return render(request, 'team_page.html', {'teams' : teams, 'tasks' : tasks_from_team, 'user': user, 'teams_members': teams_members,})

@login_required
def dashboard(request):
    """Display the current user's dashboard."""
    if request.session.get('team'):
        del request.session['team']
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

    return render(request, 'dashboard.html', {'user': current_user, 'team_invites': team_names, 'invites': invite_list, 'teams' : teams, 'tasks' : tasks})

@login_required
def add_members(request):
    if request.method == 'POST':
        form = InviteForm(request.POST) 
        if form.is_valid():
            team_id = request.session.get('team')
            form.save_invites(team_id=team_id)
            del request.session['team']
            return redirect('dashboard'); 
    else:
        form = InviteForm()
    return render(request, "add_members.html", {'form': form})
@login_required

@login_required
def team_creation(request):
    if request.method == 'POST':
        form = TeamCreationForm(request.POST, request.FILES) 
        if form.is_valid():
            team = form.save(commit=False)
            team.team_leader = request.user
            team.save()
            request.session['team'] = team.team_id
            team.team_members.set([request.user])
            team.save
            return redirect('add_members'); 
    else:
        form = TeamCreationForm()
    return render(request, "team_creation.html", {'form': form})




@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')


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
def create_task(request):
    team_id = request.session.get('team')
    if request.method == 'POST':
        form = TaskForm(team_id, request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit = False)
            task.created_by = request.user
            assigned_to_user = form.cleaned_data.get('assigned_to')
            task.save()
            task.assigned_to.set(assigned_to_user)
            task.related_to_team = Team.objects.get(team_id = team_id)
            task.save()
            return redirect('team_page', team_id = team_id)
    else: 
        form = TaskForm(team_id)
    return render(request, 'task.html', {'form' : form})

@login_required
def edit_task(request, task_id):
    team_id = request.session.get('team')
    task = Task.objects.get(pk=task_id)
    if request.method == 'POST':
        form = TaskForm(team_id, request.POST, request.FILES, instance=task)
        if form.is_valid():
            task = form.save()
            task.total_hours_worked = task.total_hours_worked + float(form.cleaned_data.get('total_hours_worked'))
            task.save()
            return redirect('team_page', team_id=team_id)
    else:
        form = TaskForm(team_id, instance=task)

    return render(request, 'edit_task.html', {'form': form})

@login_required
def delete_task(request, task_id):
    team_id = request.session.get('team')
    task = Task.objects.get(pk = task_id)
    task.delete()
    return redirect('team_page', team_id = team_id)

@login_required
def view_task(request, task_id):
    task = Task.objects.get(pk=task_id)
    team_id = request.session.get('team')
    # Handle POST request for updating hours worked
    if request.method == 'POST':
        form = TaskForm(team_id, request.POST, instance=task)
        if form.is_valid():
            form.save()
            task.total_hours_worked = sum(form.cleaned_data.get(f'user_{user.id}_hours_worked', 0.0) for user in task.assigned_to.all())
            task.save()
            return redirect('view_task', task_id=task_id)
    else:
        form = TaskForm(team_id, instance = task)

    return render(request, 'view_task.html', {'task': task, 'form': form})
    
