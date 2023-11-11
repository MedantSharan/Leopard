from django.contrib import admin
from .models import Team,Team_Members,Invites, User
# Register your models here.
admin.site.register(Team)
admin.site.register(Team_Members)
admin.site.register(Invites)
admin.site.register(User)