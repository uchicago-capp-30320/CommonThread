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
"""
from django.contrib import admin
from django.urls import path
from ct_application.views import home_test, show_org_dashboard, show_project_dashboard, get_story 

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",home_test, name="home_test"),
    path("stories/",get_story, name="get_stories"),
    path("stories/<int:story_id/",get_story, name="get_story"),
    path("org/<int:org_id>/<int:user_id>/", show_org_dashboard, name="show_org_dashboard"),
    path("org/<int:org_id>/<int:user_id>/project/<int:project_id>/", show_project_dashboard, name="show_project_dashboard"),
]
