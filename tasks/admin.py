from django.contrib import admin
from .models import Task, Team,Team_Members,Invites, User

admin.site.register(Task)

admin.site.register(Team)
admin.site.register(Team_Members)
admin.site.register(Invites)
admin.site.register(User)
