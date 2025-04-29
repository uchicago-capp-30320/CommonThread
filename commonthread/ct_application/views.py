from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseForbidden
from .models import User, Organization, OrgUser, Project, Story, ProjectTag # This is how we query data from the database 
# the names of the models may change on a different branch.


# Create your views here.

def home_test(request):
    return HttpResponse("Welcome to the Common Threads Home Page!", status=200)

def show_project_dashboard(request, user_id, org_id, project_id):
    # check user org and project IDs are provided
    if not all([user_id, org_id, project_id]):
        return HttpResponseNotFound(
            "User ID, Organization ID, or Project ID not provided.",
            status=404
        )
    # load user and org or throw 404 if not found
    user = get_object_or_404(User,   pk=user_id)
    org  = get_object_or_404(Organization, pk=org_id)

    # check if user is indeed a member of the org
    try:
        membership = OrgUser.objects.get(user=user, org=org)
    except OrgUser.DoesNotExist:
        return HttpResponseForbidden(
            "You are not a member of this organization! Not authorized.",
            status=403
        )

    # project may not belong to the org, so check that too
    project = get_object_or_404(Project, pk=project_id)
    if project.org_id != org.id:
        return HttpResponseNotFound(
            "Project does not belong to this organization. Not authorized.",
            status=404
        )

    # how will this access level be defined? admin, curator, member?
    # if not (
    #     membership.access_level == "admin"
    #     or project.curator == user.id
    # ):
    #     return HttpResponseForbidden(
    #         "Insufficient access level to view this project.",
    #         status=403
    #     )

    # load whatever data you need for the dashboard and send to frontend
    story_count = Story.objects.filter(proj=project).count()
    tag_count   = ProjectTag.objects.filter(proj=project).count()
    data= {
        "user": user,
        "org": org,
        "project": project,
        # Add any other data you need for the dashboard
    }   

    return JsonResponse({
        "project_id":  project.id,
        "story_count": story_count,
        "tag_count":   tag_count,
    }, status=200)