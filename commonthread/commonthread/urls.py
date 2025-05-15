"""
URL configuration for commonthread project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

Refs:
- https://learndjango.com/tutorials/django-login-and-logout-tutorial
"""

from django.contrib import admin
from django.urls import path, include
from ct_application.views import (
    home_test,
    login,
    get_new_access_token,
    create_user,
    get_user, #show_user_dashboard
    get_user_detail,
    edit_user,
    delete_user,
    create_org,
    get_org, #show_org_dashboard, the new get-stories
    get_org_admin, #show_org_admin dasboard
    get_org_projects,
    edit_org,
    delete_org,
    add_user_to_org,
    delete_user_from_org,
    create_project,
    get_project, #show_project_dashboard
    edit_project,
    delete_project,
    get_story,
    create_story,
    edit_story,
    delete_story

)

urlpatterns = [
    path("", home_test, name="home"),  # GET /
    path("login", login, name="login"),
    path("create_access", get_new_access_token, name="access-create"),

    #User Related Endpoints
    path("user/create", create_user, name="user-create"),
    path("user/<int:user_id>/dashboard", get_user, name="user-dashboard"),
    path("user/<int:user_id>/admin", get_user_detail, name="user-details"),
    path("user/<int:user_id>/edit", edit_user, name="user-edit"),
    path("user/<int:user_id>/delete", delete_user, name="user-delete"),
    
    #Org Related Endpoints
    path("org/create", create_org, name="org-create"),
    path("org/<int:org_id>", get_org, name="org-dashboard"),
    path(
        "org/<int:org_id>/user-admin",
        get_org_admin,
        name="org-admin-dashboard",
    ),
    path("org/<int:org_id>/project-admin", get_org_projects, name="org-projects"),
    path("org/<int:org_id>/edit", edit_org, name="org-edit"),
    path("org/<int:org_id>/delete", delete_org, name="org-delete"),
    path("org/<int:org_id>/add-user", add_user_to_org, name="add-user-to-org"),
    path(
        "/org/<int:org_id>/delete-user", 
         delete_user_from_org, 
         name="delete-user-from-org"),

    #Project Related Endpoints
    path("project/create", create_project, name="project-create"),
    path("project/<int:project_id>", get_project, name="project-dashboard"),
    path("project/<int:project_id>/edit", edit_project, name="project-edit"),
    path("project/<int:project_id>/delete", delete_project, name="project-delete"),
    
    #Story Related Endpoints
    path("story/create", create_story, name="story-create"),
    path("story/<int:story_id>", get_story, name="story-detail"),
    path("story/<int:story_id>/edit", edit_story, name="story-edit"),
    path("story/<int:story_id>/delete", delete_story, name="story-delete"),
    # TODO add a bulk‑create endpoint if needed

    path("admin/", admin.site.urls), # UNUSED- REMOVE?
    path("accounts/", include("django.contrib.auth.urls")),  # UNUSED- REMOVE?
]
