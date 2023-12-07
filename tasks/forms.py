"""Forms for the tasks app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
import datetime
from django.core.validators import MinValueValidator
from .models import User,Team,Invites, Task

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )
        return user

class DateInput(forms.DateInput):
    input_type = 'date'

class TaskForm(forms.ModelForm):
    """Form to create tasks"""

    assigned_to = forms.ModelMultipleChoiceField(queryset=User.objects.none(), required=True, label='Assign to user', widget=forms.SelectMultiple())
    due_date = forms.DateField(widget = DateInput, validators=[MinValueValidator(datetime.date.today)], required = False)
    
    def __init__(self, team_id, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        team_members = User.objects.filter(member_of_team__team_id=team_id)
        self.fields['assigned_to'].queryset = team_members

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'assigned_to']
        widgets = {'description' : forms.Textarea()} 


class TeamCreationForm(forms.ModelForm):
     class Meta:
        """Form options."""

        model = Team
        fields = ['team_name', 'team_description']

class InviteForm(forms.Form):
    """Form enabling team leaders to add members."""
    usernames = forms.CharField(
        label="Enter usernames (comma-separated)",
        max_length=100
    )

    def __init__(self, *args, **kwargs):
        """Construct a new form instance with a team id instance"""
        team_id = kwargs.pop('team_id', None)
        super(InviteForm, self).__init__(*args, **kwargs)
        self.team_id = team_id

    def getUsernames(self):
        """Gets all listed usernames"""
        usernames = self.cleaned_data['usernames'].split(',')
        unique_usernames = set(username.strip() for username in usernames)
        return list(unique_usernames)


    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()
        usernames = self.getUsernames()
        for username in usernames:
            try:
                user = User.objects.get(username=username)
                team =Team.objects.get(team_id = self.team_id)
                if(team.team_members.filter(username = user).exists() or team.team_leader == user):
                    self.add_error('usernames', f"User '{username}' is already in this team")
                elif(Invites.objects.filter(team_id = self.team_id, username = user).exists()):
                    self.add_error('usernames', f"User '{username}' has already been sent an invite to this team")
            except User.DoesNotExist:
                self.add_error('usernames', f"User '{username}' doesn't exist")
        

    def save_invites(self, team_id):
        """Creates an invite for each valid user listed"""
        usernames = self.getUsernames()
        for username in usernames:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                continue

            Invites.objects.create(
                username = user,
                team_id = team_id,
            )





