import json
from datetime import date
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest
from .utils import generate_access_token, generate_refresh_token
from django.contrib.auth import get_user_model
from .models import Organization, OrgUser, Project, Story, Tag, ProjectTag, UserLogin

User = get_user_model()
# the names of the models may change on a different branch.


# Create your views here.
@ensure_csrf_cookie # Need this for POSTMAN testing purposes. Otherwise
# CSRF token is not received in a single GET and POST requests fail.
def home_test(request):
    return HttpResponse("Welcome to the Common Threads Home Page!", status=200)

def login(request): 
    """
    TODO: Incorporate JWT
    """
    authorized = True
    if authorized: 
        return HttpResponse("Login successful", status=200)
    return HttpResponse("Login usuccesfful", status=403)


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
        _ = OrgUser.objects.get(user_id=user, org_id=org)
    except OrgUser.DoesNotExist:
        return HttpResponseForbidden(
            "You are not a member of this organization! Not authorized.",
            status=403
        )

    # project may not belong to the org, so check that too
    project = get_object_or_404(Project, pk=project_id)
    if project.org_id != org:
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
    story_count = Story.objects.filter(proj_id=project).count()
    tag_count   = ProjectTag.objects.filter(proj_id=project).count()
    # data= {
    #     "user": user,
    #     "org": org,
    #     "project": project,
    #     # Add any other data you need for the dashboard
    # }   

    return JsonResponse({
        "project_id":  project.proj_id,
        "story_count": story_count,
        "tag_count":   tag_count,
    }, status=200)

def show_org_dashboard(request, user_id, org_id):
    # check user org and project IDs are provided
    if not all([user_id, org_id]):
        return HttpResponseNotFound(
            "User ID or Organization ID not provided.",
            status=404
        )
    # load user and org or throw 404 if not found
    user = get_object_or_404(User,   pk=user_id)
    org  = get_object_or_404(Organization, pk=org_id)

    # check if user is indeed a member of the org
    try:
        _ = OrgUser.objects.get(user_id=user, org_id=org)
    except OrgUser.DoesNotExist:
        return HttpResponseForbidden(
            "You are not a member of this organization! Not authorized.",
            status=403
        )

    # get all projects for the organization
    projects = Project.objects.filter(org_id=org)
    project_count = projects.count()

    # data= {
    #     "user": user,
    #     "org": org,
    #     "projects": projects,
    # }   

    return JsonResponse({
        "organization_id": org.org_id,
        "organization_name": org.name,
        "project_count": project_count,
    }, status=200)

###############################################################################
@require_GET
#TODO authentication and authorization check
def get_story(request,story_id = None):
    if story_id:
        try:
            story = Story.objects.get(story_id = story_id)
            return JsonResponse({
                "story_id": story.story_id,
                "storyteller": story.storyteller,
                "curator":story.curator.user_id if story.curator else None,
                "date": story.date,
                "content": story.content
            }, status = 200)
        except Story.DoesNotExist:
            return HttpResponseNotFound(
            "Could not find that story. It has been either deleted or misplaced",
            status=404
        )
    else:
        try:
            #TODO Decide if all the details are needed if all stories are asked for
            stories = Story.objects.all()
            return JsonResponse({
                'stories': list(stories.values("story_id","storyteller","curator","date","content"))
            },status = 200)
        except Exception as e:
            return JsonResponse({"success": False, "error":str(e)}, status = 500)


###############################################################################

@require_POST
def create_user(request):
    """ 
    Receives a request with user_id, username and password values in its body 
    and registers new user in the login table of the db. 
    # TODO: Check that user is does not already exists 
    # TODO: Send email confirmation 
    # TODO: Update docstrings and specify exceptions 
    """
    try:
        user_data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    
    # Check that all required keys are in the request 
    required_keys = ["user_id", "username", "password"]
    missing_keys = [key for key in required_keys if key not in user_data]

    if missing_keys: 
        return JsonResponse(
            {"success": False, 
             "error":f"The following required keys are missing: {missing_keys}"})

    # Update Django model  
    try: 
        UserLogin.objects.create(
            user_id = user_data["user_id"], 
            username = user_data["username"], 
            password = user_data["password"]
        )
    except Exception as e: 
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)



###############################################################################

@require_POST
def add_user_to_org(request):
    """ 
    Receives a request with user_id and org_id its body and registers new user 
    user-org relationship in the login table of the db. 
    # TODO: Update docstrings and specify exceptions 
    """
    try:
        org_user_data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    
    # Check that all required keys are in the request 
    required_keys = ["user_id", "org_id"]
    missing_keys = [key for key in required_keys if key not in org_user_data]

    if missing_keys: 
        return JsonResponse(
            {"success": False, 
             "error":f"The following required keys are missing: {missing_keys}"})

    if "access" in org_user_data: 
        access = org_user_data["access"]
    else: 
        access = None
    try: 
        OrgUser.objects.create(
            user_id = org_user_data["user_id"], 
            org_id = org_user_data["org_id"],
            access = org_user_data["access"]
        )
    except Exception as e: 
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)


###############################################################################
@require_POST
#TODO authentication and authorization check
def create_story(request):
    try:
        #TODO connect story to a project
        story_data = json.loads(request.body)
        _ = Story.objects.create(
            story_id    = story_data["story_id"],
            storyteller = story_data["storyteller"],
            curator_id  = story_data["curator"],
            date        = story_data["date"],
            content     = story_data["content"],
            proj_id_id  = story_data["proj_id"],
            org_id_id   = story_data["org_id"],
        )
        return JsonResponse({
            "story_id": story_data.get("story_id")
        }, status = 200)
    
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)
    
###############################################################################
@require_POST
#TODO authentication and authorization check
def create_project(request):

    try:
        project_data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    org_id = project_data.get('org_id')
    if not org_id:
        return JsonResponse({
            "success": False,
            "error": 'Organization is required'
        }, status=400)
    
    #Need to get org as object to pass to the project creation
    try:
        org = Organization.objects.get(pk=org_id)
    except Organization.DoesNotExist:
        return JsonResponse({"success": False, "error": "Organization not found"}, status=404)
    
    try:
        project = Project.objects.create(
            name=project_data['name'],
            curator_id=project_data['curator'],
            org_id=org,
            date=project_data.get('date', str(date.today()))
        )

        # move the tag loop inside the try
        tags = project_data.get('tags', [])
        for tag_name in tags:
            tag = Tag.objects.create(name=tag_name)
            ProjectTag.objects.create(
                tag_id=tag,
                proj_id=project,
            )

        return JsonResponse({
            'success': True,
            'project_id': project.proj_id,
        }, status=201)
    except KeyError as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"success": False,
                            "error": f"internal service error {e}"}, status=500)


###############################################################################

@require_POST
#TODO authentication and authorization check
def create_org(request):
    org_data = json.loads(request.body)
    try:
        org = Organization.objects.create(
            name=org_data['name'],
            org_id=org_data['org_id'],
        )
        user= get_user_model().objects.get(pk=org_data['user_id'])
        OrgUser.objects.create(
            org_id=org,
            user_id=user,
            access="admin"
        )
    except KeyError as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success":False,
            "error": f"internal service error{str(e)}"
        }, status = 500)
    
    return JsonResponse({
            'success': True,
            'org_id': org.org_id,
        }, status=201)

###############################################################################
@require_GET
# TODO authentication and authorization check
def show_user_dashboard(request, user_id):
    try:
        user = User.objects.get(pk=user_id)

        org_memberships = OrgUser.objects.filter(user_id=user_id).select_related(
            "org_id"
        )

        orgs_data = [
            {
                "org_id": membership.org_id.org_id,
                "org_name": membership.org_id.name,
                "access": membership.access,
            }
            for membership in org_memberships
        ]

        return JsonResponse(
            {
                "user_id": user.user_id,
                "user_name": user.name,
                "organizations": orgs_data,
            },
            status=200,
        )

    except User.DoesNotExist:
        return HttpResponseNotFound("User not found.")


###############################################################################
@require_http_methods(["GET", "POST"])
def show_org_admin_dashboard(request, user_id, org_id):
    try:
        requester_membership = OrgUser.objects.get(user_id=user_id, org_id=org_id)
    except OrgUser.DoesNotExist:
        return HttpResponseForbidden("User is not a member of the organization.")

    # get method for seeing users in org
    if request.method == "GET":
        org_members = OrgUser.objects.filter(org_id=org_id).select_related("user_id")

        data = [
            {
                "user_id": member.user_id.user_id,
                "user_name": member.user_id.name,
                "access": member.access,
            }
            for member in org_members
        ]

        return JsonResponse(
            {"org_id": org_id, "requested_by": user_id, "organization_users": data}
        )

    # post method for updating access level
    elif request.method == "POST":
        if requester_membership.access != "admin":
            return HttpResponseForbidden("Only admins can change access levels.")

        try:
            body = json.loads(request.body)
            target_user_id = body.get("target_user_id")
            new_access = body.get("new_access")

            if not target_user_id or not new_access:
                return HttpResponseBadRequest("Missing target_user_id or new_access.")

            target_membership = OrgUser.objects.get(
                user_id=target_user_id, org_id=org_id
            )
            target_membership.access = new_access
            target_membership.save()

            return JsonResponse(
                {
                    "message": "Access level updated.",
                    "user_id": target_user_id,
                    "new_access": new_access,
                },
                status=200,
            )

        except OrgUser.DoesNotExist:
            return HttpResponseNotFound(
                "Target user is not a member of this organization."
            )
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON.")

#### EOF. ####