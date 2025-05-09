import logging
import json
from datetime import date
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.http import (
    HttpResponse,
    JsonResponse,
    HttpResponseNotFound,
    HttpResponseForbidden,
    HttpResponseBadRequest,
)
from .utils import generate_access_token, generate_refresh_token, decode_refresh_token
from django.contrib.auth import authenticate, get_user_model
from .models import Organization, OrgUser, Project, Story, Tag, ProjectTag, StoryTag, CustomUser
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from django.utils import timezone

User = get_user_model()
# the names of the models may change on a different branch.


# Create your views here.
@ensure_csrf_cookie  # Need this for POSTMAN testing purposes. Otherwise
# CSRF token is not received in a single GET and POST requests fail.
def home_test(request):
    return HttpResponse("Welcome to the Common Threads Home Page!", status=200)

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def login(request): #need not pass username and password as query params
    """
    Authenticate user and return JWT access & refresh tokens.
    Falls back to request.POST if body isnt valid JSON.
    """
    logger.debug("LOGIN ➤ content-type=%r body=%r", request.content_type, request.body)
    # parse JSON or form
    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)
        except Exception as e:
            logger.debug("LOGIN ➤ JSON parse failed: %r", e)
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    else:
        data = request.POST
        logger.debug("LOGIN ➤ form-data: %r", data)

    username = data.get("username")
    password = data.get("password")
    logger.debug("LOGIN ➤ extracted username=%r password=%r", username, password)

    if not username or not password:
        return JsonResponse(
            {"success": False, "error": "Username and password are not provided"},
            status=400,
        )
    
    authenticated_user = authenticate(username=username, password=password)
    logger.debug("LOGIN ➤ authenticate returned %r", authenticated_user)

    if authenticated_user is None:
        return JsonResponse(
            {"success": False, "error": "Invalid username or password"}, status=403
        )

    access_token= generate_access_token(authenticated_user.user_id)
    refresh_token = generate_refresh_token(authenticated_user.user_id)

    return JsonResponse(
        {"success": True, 
         "access_token": access_token, 
         "refresh_token": refresh_token
         }, 
         status=200
    )

@require_POST
def get_new_access_token(request):
    # TODO change this if they will send it in as a cookie 
    logger.debug("REFRESH ➤ content-type=%r body=%r", request.content_type, request.body)

    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)
        except Exception as e:
            logger.debug("REFRESH ➤ JSON parse failed: %r", e)
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    else:
        data = request.POST
        logger.debug("REFRESH ➤ form-data: %r", data)

    refresh_token = data.get("refresh_token")
    logger.debug("REFRESH ➤ got refresh_token=%r", refresh_token)
    if not refresh_token:
        return JsonResponse({"success": False,"error": "Refresh token required"}, status=400)
    
    try:
        decoded_refresh = decode_refresh_token(refresh_token)
        logger.debug("REFRESH ➤ decoded payload: %r", decoded_refresh)
        user_id = decoded_refresh.get("sub")
        new_access_token = generate_access_token(user_id)
        return JsonResponse({"success":True,"access_token": new_access_token})
    except ExpiredSignatureError:
        # we need to redirect to login? Onur says we can't do this, frontend should handle it
        logger.debug("REFRESH ➤ expired")
        return JsonResponse({"success": False,"error": "Refresh token expired"}, status=401)
    except InvalidTokenError:
        # we need to redirect to login? Onur says we can't do this, frontend should handle it
        logger.debug("REFRESH ➤ invalid")
        return JsonResponse({"success": False,"error": "Invalid refresh token"}, status=401)
    except Exception:
        # catch anything else (e.g. wrong payload shape)
        return JsonResponse(
            {"success": False, "error": "Unable to refresh token"}, 
            status=400
        )

def show_project_dashboard(request, user_id, org_id, project_id):
    # check user org and project IDs are provided
    if not all([user_id, org_id, project_id]):
        return HttpResponseNotFound(
            "User ID, Organization ID, or Project ID not provided.", status=404
        )
    # load user and org or throw 404 if not found
    user = get_object_or_404(User, pk=user_id)
    org = get_object_or_404(Organization, pk=org_id)

    # check if user is indeed a member of the org
    try:
        _ = OrgUser.objects.get(user_id=user, org_id=org)
    except OrgUser.DoesNotExist:
        return HttpResponseForbidden(
            "You are not a member of this organization! Not authorized.", status=403
        )

    # project may not belong to the org, so check that too
    project = get_object_or_404(Project, pk=project_id)
    if project.org_id != org:
        return HttpResponseNotFound(
            "Project does not belong to this organization. Not authorized.", status=404
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
    tag_count = ProjectTag.objects.filter(proj_id=project).count()
    # data= {
    #     "user": user,
    #     "org": org,
    #     "project": project,
    #     # Add any other data you need for the dashboard
    # }

    return JsonResponse(
    {
        "project_id": project.id, 
        "story_count": story_count,
        "tag_count": tag_count,
    },
    status=200,
)   


def show_org_dashboard(request, user_id, org_id):
    # check user org and project IDs are provided
    if not all([user_id, org_id]):
        return HttpResponseNotFound(
            "User ID or Organization ID not provided.", status=404
        )
    # load user and org or throw 404 if not found
    user = get_object_or_404(User, pk=user_id)
    org = get_object_or_404(Organization, pk=org_id)

    # check if user is indeed a member of the org
    try:
        _ = OrgUser.objects.get(user_id=user, org_id=org)
    except OrgUser.DoesNotExist:
        return HttpResponseForbidden(
            "You are not a member of this organization! Not authorized.", status=403
        )

    # get all projects for the organization
    projects = Project.objects.filter(org_id=org)
    project_count = projects.count()

    # data= {
    #     "user": user,
    #     "org": org,
    #     "projects": projects,
    # }

    return JsonResponse(
        {
            "organization_id": org.org_id,
            "organization_name": org.name,
            "project_count": project_count,
        },
        status=200,
    )


###############################################################################
@require_GET
# TODO authentication and authorization check
def get_story(request, story_id=None):
    if story_id:
        try:
            story = Story.objects.select_related('proj_id').get(id=story_id)
            
            story_tags = StoryTag.objects.filter(story_id=story).select_related('tag_id')
            tags = [{
                'name': st.tag_id.name,
                'value': st.tag_id.value
            } for st in story_tags]
            
            return JsonResponse(
                {
                    "story_id": story.id,
                    "project_id": story.proj_id.id,
                    "project_name": story.proj_id.name,
                    "storyteller": story.storyteller,
                    "curator": story.curator.user_id if story.curator else None,
                    "date": story.date,
                    "content": story.content,
                    "tags": tags
                },
                status=200,
            )
        except Story.DoesNotExist:
            return HttpResponseNotFound(
                "Could not find that story. It has been either deleted or misplaced",
                status=404,
            )
    else:
        try:
            # Get all stories with their tags and projects
            stories = Story.objects.select_related('proj_id').all()
            stories_data = []
            
            for story in stories:
                story_tags = StoryTag.objects.filter(story_id=story).select_related('tag_id')
                tags = [{
                    'name': st.tag_id.name,
                    'value': st.tag_id.value
                } for st in story_tags]
                
                stories_data.append({
                    "story_id": story.id,
                    "storyteller": story.storyteller,
                    "project_id": story.proj_id.id,
                    "project_name": story.proj_id.name,
                    "curator": story.curator.user_id if story.curator else None,
                    "date": story.date,
                    "content": story.content,
                    "tags": tags
                })
            
            return JsonResponse(
                {
                    "stories": stories_data
                },
                status=200,
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)


###############################################################################


@require_POST
def create_user(request):
    """
    Receives a request with user_id, username and password values in its body
    and registers new user in the login table of the db.
    # TODO: Check that user is does not already exists
    # TODO: Send email confirmation
    # TODO: Update docstrings and specify exceptions

    Ref: https://docs.djangoproject.com/en/5.2/topics/auth/default/
    """
    try:
        user_data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    username = user_data.get("username")
    password = user_data.get("password")
    if not username or not password:
        return JsonResponse(
            {"success": False, "error": "Username and password are required"},
            status=400,
        )

    #  check for existing user
    if User.objects.filter(username=username).exists():
        return JsonResponse(
            {"success": False, "error": "Username already exists"}, status=400
        )
    
    try:
        #this needs to be CustomUser
        CustomUser.objects.create_user(
            username=username,
            password=password,
            first_name=user_data.get("first_name", ""),
            last_name=user_data.get("last_name", ""),
            email=user_data.get("email", ""),
            name=user_data.get("name", ""),
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


    #try: #### SUNSET IN FAVOR OF DJANGO PASSWORD STORAGE #####
    #    UserLogin.objects.create(
    #        user_id=django_user,
    #        username=username,
    #        password=password,  # or better: store a hash
    #    )
    #except Exception as e:
    #    # if this fails you might want to roll back the django_user you just made
    #    return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": True}, status=201)


###############################################################################


@require_POST
def add_user_to_org(request):
    """
    Receives a request with user_id and org_id its body and registers new user
    user-org relationship in the login table of the db.
    # TODO: Update docstrings and specify exceptions
    """
    try:
        org_user_data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    # Check that all required keys are in the request
    required_keys = ["user_id", "org_id"]
    missing_keys = [key for key in required_keys if key not in org_user_data]

    if missing_keys:
        return JsonResponse(
            {
                "success": False,
                "error": f"The following required keys are missing: {missing_keys}",
            }
        )

    # TODO: Get organization auth
    try:
        OrgUser.objects.create(
            user_id=org_user_data["user_id"],
            org_id=org_user_data["org_id"],
            access=org_user_data["access"],
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"success": True}, status=201)


###############################################################################
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def create_story(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    try:
        print("Received request body:", request.body)
        story_data = json.loads(request.body)
        print("Parsed story data:", story_data)
        
       
        try:
            project = Project.objects.get(id=story_data["proj_id"])
            print("Found project:", project)
        except Project.DoesNotExist:
            print(f"Project with ID {story_data['proj_id']} does not exist")
            return JsonResponse({"error": f"Project with ID {story_data['proj_id']} does not exist"}, status=400)
        
        
       
        print("Curator ID:", story_data.get("curator"))
        
        try:
            story = Story.objects.create(
                storyteller=story_data["storyteller"],
                curator_id=story_data.get("curator"),
                date=timezone.now(),
                content=story_data["content"],
                proj_id=project,
            )
            print("Created story:", story)
        except Exception as e:
            print("Error creating story:", str(e))
            print("Error type:", type(e))
            import traceback
            print("Traceback:", traceback.format_exc())
            raise

        if "tags" in story_data:
            for tag_data in story_data["tags"]:
                tag, _ = Tag.objects.get_or_create(
                    name=tag_data["name"],
                    value=tag_data["value"]
                )
                StoryTag.objects.create(story_id=story, tag_id=tag)
                print("Created tag:", tag)

        return JsonResponse({"story_id": story.id}, status=200)
    except Exception as e:
        print("Error creating story:", str(e))
        print("Error type:", type(e))
        import traceback
        print("Traceback:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=400)


###############################################################################
@require_POST
# TODO authentication and authorization check
def create_project(request):

    try:
        project_data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    org_id = project_data.get("org_id")
    if not org_id:
        return JsonResponse(
            {"success": False, "error": "Organization is required"}, status=400
        )

    # Need to get org as object to pass to the project creation
    try:
        org = Organization.objects.get(pk=org_id)
    except Organization.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Organization not found"}, status=404
        )

    try:
        project = Project.objects.create(
            name=project_data["name"],
            curator_id=project_data["curator"],
            org_id=org,
            date=project_data.get("date", str(date.today())),
        )

        # move the tag loop inside the try
        tags = project_data.get("tags", [])
        for tag_name in tags:
            tag = Tag.objects.create(name=tag_name)
            ProjectTag.objects.create(
                tag_id=tag,
                proj_id=project,
            )

        return JsonResponse(
            {
                "success": True,
                "project_id": project.id,
            },
            status=201,
        )
    except KeyError as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"internal service error {e}"}, status=500
        )


###############################################################################


@require_POST
# TODO authentication and authorization check
def create_org(request):
    org_data = json.loads(request.body)
    try:
        org = Organization.objects.create(
            name=org_data["name"],
            org_id=org_data["org_id"],
        )
        user = get_user_model().objects.get(pk=org_data["user_id"])
        OrgUser.objects.create(org_id=org, user_id=user, access="admin")
    except KeyError as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"internal service error{str(e)}"}, status=500
        )

    return JsonResponse(
        {
            "success": True,
            "org_id": org.org_id,
        },
        status=201,
    )


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
