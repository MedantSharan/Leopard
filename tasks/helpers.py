from django.conf import settings
from django.shortcuts import redirect
# from django.shortcuts import send_mail
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def login_prohibited(view_function):
    """Decorator for view functions that redirect users away if they are logged in."""
    
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function

# def send_task_assignment_notification(email, task):
#     """Send a notification email for a task assignment."""
    
#     subject = f'You have been assigned a new task: {task.title}'
#     message = f'Due date: {task.due_date}\nTask description: {task.description}'
#     from_email = 'your-email@example.com'
#     recipient_list = [email]

#     send_mail(subject, message, from_email, recipient_list)

# def send_task_assignment_notification(receiver_email, task):
#     """Send a task assignment email notification."""
#     subject = f"You've been assigned a new task: {task.title}"
#     html_message = render_to_string('task_assignment_email.html', {'task': task})
#     plain_message = strip_tags(html_message)

#     send_mail(
#         subject,
#         plain_message,
#         'your-sender-email@example.com',  # Update with your email address
#         [receiver_email],
#         html_message=html_message,
#     )

def send_task_assignment_notification(receiver_email, task):
    """Send a task assignment email notification."""
    subject = f"You've been assigned a new task: {task.title}"
    html_message = render_to_string('task_assignment_email.html', {'task': task})
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        'your-sender-email@example.com',
        [receiver_email],
        html_message=html_message,
    )