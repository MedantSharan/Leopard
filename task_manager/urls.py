"""
URL configuration for task_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('create_task/', views.create_task, name = 'create_task'),
    path('edit_task/<int:task_id>', views.edit_task, name = 'edit_task'),
    path('delete_task/<int:task_id>', views.delete_task, name = 'delete_task'),
    path('team_creation/', views.team_creation, name = "team_creation"),
    path('add_members/', views.add_members, name = "add_members"),
    path('team_page/<int:team_id>', views.team_page, name = "team_page"),
    path('join_team/<int:team_id>', views.join_team, name = 'join_team'),
    path('decline_team/<int:team_id>', views.decline_team, name = 'decline_team'),
]
