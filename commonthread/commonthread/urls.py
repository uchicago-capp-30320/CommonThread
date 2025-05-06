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
    create_user,
    create_project,
    add_user_to_org,
    get_story,
    create_story,
    show_org_dashboard,
    create_org,
    show_project_dashboard,
    show_user_dashboard,
    show_org_admin_dashboard,
    get_new_access_token,
)

urlpatterns = [
    path("", home_test, name="home"),  # GET /
    path("login", login, name="login"),
    path("login/create_access", get_new_access_token, name="access-create"),
    path("user/create", create_user, name="user-create"),
    path("project/create", create_project, name="project-create"),
    path("project/add_user", add_user_to_org, name="add-user-to-rpoject"),
    path("stories/", get_story, name="story-list"),  # GET all
    path("stories/<int:story_id>/", get_story, name="story-detail"),  # GET one
    path("stories/create/", create_story, name="story-create"),  # POST one
    # TODO add a bulk‑create endpoint if needed
    path("org/<int:user_id>/<int:org_id>/", show_org_dashboard, name="org-dashboard"),
    path("org/create/", create_org, name="org-create"),
    path(
        "org/<int:user_id>/<int:org_id>/project/<int:project_id>/",
        show_project_dashboard,
        name="project-dashboard",
    ),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # new
    path("user/<int:user_id>/dashboard/", show_user_dashboard, name="user_dashboard"),
    path(
        "org/<int:org_id>/admin/<int:user_id>/",
        show_org_admin_dashboard,
        name="org_admin_dashboard",
    ),
]
