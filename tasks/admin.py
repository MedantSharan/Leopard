from django.contrib import admin
from .models import Task, Team,Invites, User

admin.site.register(Task)

admin.site.register(Team)
admin.site.register(Invites)
admin.site.register(User)
