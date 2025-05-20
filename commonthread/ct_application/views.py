import logging
import json
from datetime import date
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.cache import cache_page
from django.http import (
    HttpResponse,
    JsonResponse,
    HttpResponseNotFound,
    HttpResponseForbidden,
    HttpResponseBadRequest,
)
from django.conf import settings
from .utils import (
    generate_s3_presigned,
    generate_access_token,
    generate_refresh_token,
    decode_refresh_token,
    decode_access_token,
)
from django.contrib.auth import authenticate, get_user_model
from .models import (
    Organization,
    OrgUser,
    Project,
    Story,
    Tag,
    ProjectTag,
    StoryTag,
    CustomUser,
)
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from django.utils import timezone
import traceback
from functools import wraps

User = get_user_model()
# the names of the models may change on a different branch.


# Create your views here.
@ensure_csrf_cookie  # Need this for POSTMAN testing purposes. Otherwise
# CSRF token is not received in a single GET and POST requests fail.
def home_test(request):
    return HttpResponse("Welcome to the Common Threads Home Page!", status=200)


logger = logging.getLogger(__name__)

########## Authentication and Authorization ##############


def verify_user(view_function):
    """
    Decorator for ensuring the user is allowed to access the application, handling JWT tokens & issues
    """

    @wraps(view_function)
    # def inner(view_function, *args, **kwargs): #kwargs has ids, but unused here. Do not remove.

    #    request = args
    def wrapper(request, *args, **kwargs):
        try:
            # Decode Given Access Token
            access_token = request.headers.get("Authorization", "")
            if not access_token or not access_token.startswith("Bearer "):
                return JsonResponse(
                    {"success": False, "error": "Token missing or malformed"},
                    status=401,
                )
            access_token = access_token.split(" ", 1)[1]
            _ = decode_access_token(access_token)
            # request.user_id = decoded["sub"] #we could return this so decoding does not happen twice
            return view_function(request, *args, **kwargs)

        except ExpiredSignatureError:
            # Expired Token: 299 Code used by front-end to know to request new one
            return JsonResponse(
                {"success": False, "error": "Access Expired"}, status=299
            )
        except InvalidTokenError:
            # Something broke in the process
            return JsonResponse({"success": False, "error": "Login Failed"}, status=401)

    return wrapper


def authorize_user(check_type: str):
    """
    Decorator designed to provide interface that simplifies links & setup for views. The If statement allows for
    individual auth functions that take varieties of input, but a single wrapper for ease of use.

    view_function: function being called
    request is pulled in via args, as it is the only
    check_type -> information given to access: can also add level of access required through this as well later
        - story: story id provided
        - project: project id provided
        - org: org id provided

    all id fields are optional, only need to include what is required.
    """

    def decorator(view_function):
        @wraps(view_function)
        def inner(request, *args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return JsonResponse({"success": False, "error": "No token"}, status=401)

            token = auth_header.split(" ", 1)[1]
            try:
                payload = decode_access_token(token)
                user_id = payload["sub"]
            except Exception:
                return JsonResponse(
                    {"success": False, "error": "Bad token"}, status=401
                )

            # Get the ids from the kwargs
            ids = kwargs
            try:
                # Reach the necessary authentication table based on the information provided by the request
                if check_type == "story":
                    logger.debug(
                        "Auth using info: user_id=%r story_id=%r",
                        user_id,
                        ids["story_id"],
                    )
                    is_auth = check_story_auth(user_id, ids["story_id"])
                elif check_type == "project":
                    # accept either project_id (new) or legacy proj_id
                    proj_id = ids.get("project_id") or ids.get("proj_id")
                    if proj_id is None:
                        logger.debug("Missing project id in kwargs: %r", ids)
                        return JsonResponse(
                            {"success": False, "error": "Missing project ID"},
                            status=400,
                        )
                    is_auth = check_project_auth(user_id, proj_id)
                elif check_type == "org":
                    logger.debug(
                        "Auth using info: user_id=%r org_id=%r", user_id, ids["org_id"]
                    )
                    is_auth = check_org_auth(user_id, ids["org_id"])
                else:
                    logger.debug(
                        "Invalid Auth checktype with check_type=%r", check_type
                    )

            except KeyError:
                logger.debug("KeyError: %r", ids)
                return JsonResponse(
                    {"success": False, "error": "Missing required ID"}, status=400
                )
            if not is_auth:
                return JsonResponse(
                    {"success": False, "error": "Not authorized"}, status=403
                )
            return view_function(request, *args, **kwargs)

        return inner

    return decorator


def check_org_auth(user_id: str, org_id: str):
    # Checks if user has access to an oranization, returns True if the link exists
    try:
        _ = OrgUser.objects.get(user_id=user_id, org_id=org_id)
        return True
    except OrgUser.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Not authorized to access page"}, status=403
        )


def check_project_auth(user_id: str, proj_id: str):
    # Checks if user has access through proj->org link, returns True if the link exists
    try:
        project = Project.objects.get(proj_id=proj_id)
        return check_org_auth(user_id, project.org_id)
    except Project.DoesNotExist:
        return JsonResponse({"Failed": False, "error": "Project not found"}, status=404)


def check_story_auth(user_id: str, story_id: str):
    # Checks if user has access through story->proj->org link, returns True if the link exists
    try:
        story = Story.objects.get(story_id=story_id)
        return check_project_auth(user_id, story.proj_id)
    except Story.DoesNotExist:
        return JsonResponse({"Failed": False, "error": "Story not found"}, status=404)


@csrf_exempt
@require_POST
def login(request):  # need not pass username and password as query params
    """
    Authenticate user and return JWT access & refresh tokens.
    Falls back to request.POST if body isnt valid JSON.
    """
    logger.debug("LOGIN ➤ content-type=%r body=%r", request.content_type, request.body)
    # parse JSON or form
    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)
            logger.debug(f"LOGIN ➤ Received the following JSON { data }")

            # Note: It turns out that Svelte sends the json data with the
            # name of the JS object that holds such data as key. So it needs
            # an extra unpacking step.
            data = data.get("post_data")
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

    access_token = generate_access_token(authenticated_user.id)
    logger.debug(f"LOGIN ➤ issued access_token={access_token}")
    refresh_token = generate_refresh_token(authenticated_user.id)

    # ───────────────────────────────────────────────────────────────
    import datetime
    import jwt
    from commonthread.settings import JWT_SECRET_KEY

    # decode *without* verifying exp, so we can inspect the claims:
    payload = jwt.decode(
        access_token,
        JWT_SECRET_KEY,
        algorithms=["HS256"],
        options={"verify_signature": True, "verify_exp": False},
    )
    iat = payload.get("iat")
    exp = payload.get("exp")
    # log both as raw seconds and as UTC datetimes
    logger.debug(
        f"JWT iat (epoch): {iat}, which is {datetime.datetime.fromtimestamp(iat, datetime.timezone.utc).isoformat()}"
    )
    logger.debug(
        f"JWT exp (epoch): {exp}, which is {datetime.datetime.fromtimestamp(exp, datetime.timezone.utc).isoformat()}"
    )
    # ───────────────────────────────────────────────────────────────

    return JsonResponse(
        {"success": True, "access_token": access_token, "refresh_token": refresh_token},
        status=200,
    )


@csrf_exempt
@require_POST
def get_new_access_token(request):
    # TODO change this if they will send it in as a cookie
    logger.debug(
        "REFRESH ➤ content-type=%r body=%r", request.content_type, request.body
    )

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
        return JsonResponse(
            {"success": False, "error": "Refresh token required"}, status=400
        )

    try:
        decoded_refresh = decode_refresh_token(refresh_token)
        logger.debug("REFRESH ➤ decoded payload: %r", decoded_refresh)
        user_id = decoded_refresh.get("sub")
        new_access_token = generate_access_token(user_id)
        return JsonResponse({"success": True, "access_token": new_access_token})
    except ExpiredSignatureError:
        # we need to redirect to login? Onur says we can't do this, frontend should handle it
        logger.debug("REFRESH ➤ expired")
        return JsonResponse(
            {"success": False, "error": "Refresh token expired"}, status=401
        )
    except InvalidTokenError:
        # we need to redirect to login? Onur says we can't do this, frontend should handle it
        logger.debug("REFRESH ➤ invalid")
        return JsonResponse(
            {"success": False, "error": "Invalid refresh token"}, status=401
        )
    except Exception:
        # catch anything else (e.g. wrong payload shape)
        return JsonResponse(
            {"success": False, "error": "Unable to refresh token"}, status=400
        )


@require_GET
def get_project(request, project_id):
    try:
        project = Project.objects.select_related("org", "curator").get(id=project_id)
        story_count = Story.objects.filter(proj=project).count()

        # Get associated ProjectTag objects
        project_tags = ProjectTag.objects.filter(proj=project)

        # Filter based on related Tag's `required` field
        required_tags = project_tags.filter(tag__required=True).values_list(
            "tag__name", flat=True
        )
        optional_tags = project_tags.filter(tag__required=False).values_list(
            "tag__name", flat=True
        )

        # Construct response
        data = {
            "project_id": project.id,
            "project_name": project.name,
            "org_id": project.org.id,
            "org_name": project.org.name,
            "date": project.date,
            "insight": project.insight,
            "curator": project.curator.name if project.curator else None,
            "required_tags": list(required_tags),
            "optional_tags": list(optional_tags),
            "stories": story_count,
        }

        return JsonResponse(data)

    except Project.DoesNotExist:
        logger.error(f"Project with id={project_id} not found.")
        return JsonResponse({"error": "Project not found."}, status=404)

    except Exception as e:
        logger.error(f"Error in get_project: {e}")
        return JsonResponse({"error": "Internal server error."}, status=500)


@require_GET
@verify_user
def get_org(request, org_id):
    try:
        org = get_object_or_404(Organization, id=org_id)

        # Get all projects in the org
        projects = Project.objects.filter(org=org)
        project_count = projects.count()
        # get all unique project ids
        project_ids = projects.values_list("id", flat=True).distinct()

        # Get all stories in those projects
        stories = Story.objects.filter(proj__in=projects)
        story_count = stories.count()

        # Collect curators from projects and stories
        project_curators = projects.values_list("curator", flat=True)
        story_curators = stories.values_list("curator", flat=True)

        user_ids = set(list(project_curators) + list(story_curators))
        users = CustomUser.objects.filter(id__in=user_ids)

        users_data = [
            {
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "position": user.position,
            }
            for user in users
        ]

        response_data = {
            "org_id": org.id,
            "name": org.name,
            "description": org.description,
            "profile_pic_path": org.profile.url if org.profile else "",
            "project_count": project_count,
            "project_ids": list(project_ids),
            "story_count": story_count,
            "users": users_data,
        }

        return JsonResponse(response_data, status=200)

    except Exception as e:
        logging.error(f"Error in get_org: {e}")
        return JsonResponse({"error": "Something went wrong."}, status=500)


@require_GET
def get_stories(request):
    try:
        # Accept only one of the parameters
        org_id = request.GET.get("org_id")
        project_id = request.GET.get("project_id")
        story_id = request.GET.get("story_id")
        user_id = request.GET.get("user_id")

        filters = {
            "org_id": org_id,
            "project_id": project_id,
            "story_id": story_id,
            "user_id": user_id,
        }
        active_filter = {k: v for k, v in filters.items() if v is not None}

        if len(active_filter) != 1:
            return JsonResponse(
                {
                    "error": "Specify exactly one of org_id, project_id, story_id, or user_id."
                },
                status=400,
            )

        id_type, id_value = next(iter(active_filter.items()))

        # Filter stories based on the input
        if id_type == "org_id":
            stories = Story.objects.filter(proj__org__id=id_value)
        elif id_type == "project_id":
            stories = Story.objects.filter(proj__id=id_value)
        elif id_type == "story_id":
            stories = Story.objects.filter(id=id_value)
        elif id_type == "user_id":
            stories = Story.objects.filter(curator__id=id_value)
        else:
            return JsonResponse({"error": "Invalid query parameter."}, status=400)

        # Prepare the output
        stories_data = []
        for story in stories.select_related("proj", "curator"):
            tags = Tag.objects.filter(storytag__story=story).values(
                "name", "value", "created_by"
            )

            stories_data.append(
                {
                    "story_id": story.id,
                    "storyteller": story.storyteller,
                    "project_id": story.proj.id,
                    "project_name": story.proj.name,
                    "curator": story.curator.name if story.curator else None,
                    "date": str(story.date),
                    "summary": story.summary,
                    "audio_path": (
                        story.audio_content.url if story.audio_content else None
                    ),
                    "image_path": (
                        story.image_content.url if story.image_content else None
                    ),
                    "text_content": story.text_content,
                    "tags": list(tags),
                }
            )

        response = {
            "id_type": [id_type],
            "id_value": [id_value],
            "stories": stories_data,
        }

        return JsonResponse(response, safe=False)

    except Exception as e:
        logger.error(f"Error in get_stories: {e}")
        return JsonResponse({"error": "Internal server error."}, status=500)


@require_GET
@cache_page(60 * 15)  # Cache for 15 minutes
# @verify_user
# @authorize_user('story','user')
def get_story(request, story_id=None):
    print(request.headers)
    if story_id:
        try:
            story = Story.objects.select_related("proj").get(id=story_id)
            project = Project.objects.get(id=story.proj_id)
            story_tags = StoryTag.objects.filter(story_id=story).select_related("tag")

            tags = []
            for st in story_tags:
                tag_obj = Tag.objects.get(id=st.tag_id)
                tag = {"name": tag_obj.name, "value": tag_obj.value}
                tags.append(tag)

            return JsonResponse(
                {
                    "story_id": story.id,
                    "project_id": story.proj_id,
                    "project_name": project.name,
                    "storyteller": story.storyteller,
                    "curator": story.curator.id if story.curator else None,
                    "date": story.date,
                    "text_content": story.text_content,
                    "tags": tags,
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
            stories = (
                Story.objects.select_related("proj")
                .prefetch_related("storytag_set__tag_id")
                .all()
            )
            stories_data = []

            for story in stories:
                story_tags = StoryTag.objects.filter(story_id=story).select_related(
                    "tag"
                )
                tags = [
                    {"name": st.tag_id.name, "value": st.tag_id.value}
                    for st in story.storytag_set.all()
                ]

                stories_data.append(
                    {
                        "story_id": story.id,
                        "storyteller": story.storyteller,
                        "project_id": story.proj_id.id,
                        "project_name": story.proj_id.name,
                        "curator": story.curator.id if story.curator else None,
                        "date": story.date,
                        "text_content": story.text_content,
                        "tags": tags,
                    }
                )

            return JsonResponse(
                {"stories": stories_data},
                status=200,
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
# @verify_user
# @authorize_user('org','user')
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
            return JsonResponse(
                {"error": f"Project with ID {story_data['proj_id']} does not exist"},
                status=400,
            )

        print("Curator ID:", story_data.get("curator"))

        try:
            story = Story.objects.create(
                storyteller=story_data["storyteller"],
                curator_id=story_data.get("curator"),
                date=timezone.now(),
                text_content=story_data["text_content"],
                proj_id=project.id,
            )
            print("Created story:", story)
        except Exception as e:
            print("Error creating story:", str(e))
            print("Error type:", type(e))
            print("Traceback:", traceback.format_exc())
            raise

        if "tags" in story_data:
            for tag_data in story_data["tags"]:
                tag, _ = Tag.objects.get_or_create(
                    name=tag_data["name"],
                    value=tag_data["value"],
                    required=tag_data["required"],
                )
                StoryTag.objects.create(story_id=story.id, tag_id=tag.id)
                print("Created tag:", tag)

        return JsonResponse({"story_id": story.id}, status=200)
    except Exception as e:
        print("Error creating story:", str(e))
        print("Error type:", type(e))
        print("Traceback:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
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
        # this needs to be CustomUser
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            first_name=user_data.get("first_name", ""),
            last_name=user_data.get("last_name", ""),
            email=user_data.get("email", ""),
            name=user_data.get("name", ""),
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

    # generate presigned upload data for this new user's profile picture
    presign = generate_s3_presigned(
        bucket_name=settings.CT_BUCKET_USER_PROFILES,
        key=f"profile-pictures/{user.id}.png",
        operation="upload",
        content_type="image/png",
        expiration=3600,
    )
    return JsonResponse(
        {
            "success": True,
            "upload": {"url": presign["url"], "fields": presign["fields"]},
        },
        status=201,
    )


@require_POST
# @verify_user
# @authorize_user('org','admin')
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


# @verify_user
# @authorize_user('org','admin')
def delete_user_from_org(request):
    pass


###############################################################################


# @verify_user
# @authorize_user('org','admin')
def edit_story(request):
    pass


# @verify_user
# @authorize_user('story','admin')
def delete_story(request):
    pass


###############################################################################
@require_POST
# @verify_user
# @authorize_user('org','admin')
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
            org_id=org.id,
            date=project_data.get("date", str(date.today())),
        )

        # move the tag loop inside the try
        tags = project_data.get("tags", [])
        for tag_name in tags:
            tag = Tag.objects.create(name=tag_name)
            ProjectTag.objects.create(
                tag_id=tag.id,
                proj_id=project.id,
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


# @verify_user
# @authorize_user('project','admin')
def edit_project(request):
    pass


# @verify_user
# @authorize_user('project','admin')
def delete_project(request):
    pass


@require_POST
# @verify_user
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


# @verify_user
# @authorize_user('org','admin')
def edit_org(request):
    pass


@verify_user
# @authorize_user('org','creator')
def delete_org(request):
    pass


@require_GET
@verify_user
def get_user(request):

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JsonResponse({"success": False, "error": "No token"}, status=401)

    token = auth_header.split(" ", 1)[1]
    try:
        payload = decode_access_token(token)
        user_id = payload["sub"]
    except Exception:
        return JsonResponse({"success": False, "error": "Bad token"}, status=401)

    try:
        user = get_object_or_404(CustomUser, id=user_id)

        # Get organizations the user belongs to
        org_users = OrgUser.objects.filter(user=user)
        orgs = [
            {
                "org_id": str(org_user.org.id),
                "org_name": org_user.org.name,
                "org_profile_pic_path": (
                    org_user.org.profile.url if org_user.org.profile else None
                ),
            }
            for org_user in org_users
        ]

        user_data = {
            "user_id": user.id,
            "name": user.name,
            "First_name": user.first_name,
            "Last_name": user.last_name,
            "Email": user.email,
            "City": user.city,
            "Bio": user.bio,
            "Position": user.position,
            "Profile_pic_path": user.profile.url if user.profile else None,
            "orgs": orgs,
        }

        return JsonResponse(user_data, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@verify_user
def get_user_detail(request, user_id):
    pass


@verify_user
def edit_user(request):
    pass


@verify_user
def delete_user(request):
    pass


@require_http_methods(["GET", "POST"])
# @verify_user
# @authorize_user('org','admin')
def get_org_admin(request, user_id, org_id):
    try:
        requester_membership = OrgUser.objects.get(user_id=user_id, org_id=org_id)
    except OrgUser.DoesNotExist:
        return HttpResponseForbidden("User is not a member of the organization.")

    # get method for seeing users in org
    if request.method == "GET":
        org_members = OrgUser.objects.filter(org_id=org_id).select_related("user")

        data = [
            {
                "user_id": member.user_id.id,
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


@verify_user
# @authorize_user('org','user')
def get_org_projects(request, org_id):
    # return JUST the list of projects within the organizaton, and a count how many stories are in each.
    pass


#### EOF. ####
