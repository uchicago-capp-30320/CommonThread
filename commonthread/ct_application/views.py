# IMPORTS ----------------------------------------------------------------------

import logging
import json
import datetime
import jwt
from commonthread.settings import JWT_SECRET_KEY
from uuid import uuid4
from datetime import date
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.cache import cache_page
from django.http import (
    HttpResponse,
    HttpRequest,
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
    MLProcessingQueue,
)
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from django.utils import timezone
from django.db import transaction
from django.db.models import Prefetch

# HANDLERES SET UP -------------------------------------------------------------
import traceback
from commonthread.settings import JWT_SECRET_KEY
from functools import wraps
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from .cloud.producer_service import QueueProducer

User = get_user_model()
# the names of the models may change on a different branch.

logger = logging.getLogger(__name__)


# VIEWS ------------------------------------------------------------------------

## Home test -------------------------------------------------------------------


# Create your views here.
@ensure_csrf_cookie  # Need this for POSTMAN testing purposes. Otherwise
# CSRF token is not received in a single GET and POST requests fail.
def home_test(request):
    return HttpResponse("Welcome to the Common Threads Home Page!", status=200)


## Authentication and Authorization --------------------------------------------


def verify_user(required_access="user"):
    """
    Decorator designed to provide interface that simplifies links & setup for
    views. The If statement allows for individual auth functions that take
    varieties of input, but a single wrapper for ease of use.

    view_function: function being called
    request is pulled in via args

    required_access -> level of access needed for an endpoints
        - creator: for delete endpoints
        - admin: for some edit and some delete endpoints
        - user: for some edit and all get endpoints
    """

    def decorator(view_function):
        @wraps(view_function)
        def inner(request, *args, **kwargs):

            # Verifying the user and storing their user ID for use/passback
            try:
                # Decode Given Access Token
                logger.debug("Request Headers: %r", request.headers)
                access_token = request.headers.get("Authorization", "")
                logger.debug("Access Token: %r", access_token)
                if not access_token:
                    return JsonResponse(
                        {"success": False, "error": "No token"},
                        status=401,
                    )
                elif not access_token.startswith("Bearer "):
                    return JsonResponse(
                        {"success": False, "error": "Token malformed"},
                        status=401,
                    )
                access_token = access_token.split(" ", 1)[1]
                decoded = decode_access_token(access_token)
                real_user_id = decoded["sub"]

            except ExpiredSignatureError:
                # Expired Token: 299 Code used by front-end to know to request new one
                return JsonResponse(
                    {"success": False, "error": "Access Expired"}, status=299
                )
            except InvalidTokenError:
                # Something broke in the process
                return JsonResponse(
                    {"success": False, "error": "Bad token"}, status=401
                )

            request.user_id = decoded["sub"]
            # Identifying what kind of request/auth level the user has for their request
            if kwargs:
                logging.debug("Kwargs used in Auth")
                auth_level, search_success = id_searcher(real_user_id, kwargs, required_access)
            else:
                logging.debug("Request used in Auth")
                try:
                    body = json.loads((request.body or "{}"))
                except:
                    logging.debug("Request failed to load")
                    return JsonResponse(
                    {"success": False, "error": "Body not loaded"}, status=400
                )
                auth_level, search_success = id_searcher(real_user_id, body, required_access)
            if search_success:
                auth_level_check(auth_level, required_access)
            else:
                return auth_level
            logger.debug("Authentication Success")
            return view_function(request, *args, **kwargs)

        return inner

    return decorator


def id_searcher(real_user_id, id_set, required_access):
    """
    id_set: keyword dictionary (kwargs)
    """

    try:
        logger.debug("request? %r", id_set)
        # Separate out user requests that don't have any additional needs beyond authenticating the user
        if "user_id" not in id_set:
            # Find the specific component of information that is needed for authorization
            if "org_id" not in id_set:
                if "project_id" not in id_set:
                    if "story_id" not in id_set:
                        return "user", True
                    else:
                        return check_story_auth(real_user_id, id_set["story_id"])
                else:
                    return check_project_auth(real_user_id, id_set["project_id"])
            else:
                return check_org_auth(real_user_id, id_set["org_id"])
        elif required_access != "user":
            logger.debug("Flag 2.1")
            # If there's a user id in there but we need admin/creator for some purpose.
            # This essentially serves as a failsafe against things that might include user ids
            if "org_id" not in id_set:
                if "project_id" not in id_set:
                    if "story_id" not in id_set:
                        return JsonResponse(
                            {"success": False, "error": "No Identifier Provided"},
                            status=400,
                        ), False
                    else:
                        return check_story_auth(real_user_id, id_set["story_id"])
                else:
                    return check_project_auth(real_user_id, id_set["project_id"])
            else:
                return check_org_auth(real_user_id, id_set["org_id"])
        else:
            return "user", True

    except:
        return JsonResponse(
            {"success": False, "error": "Identifier read failed"}, status=400
        ), False


def check_org_auth(user_id: str, org_id: str):
    # Checks if user has access to an organization, returns True if the link exists
    try:
        row = OrgUser.objects.get(user_id=user_id, org_id=org_id)
        return row.access, True
    except OrgUser.DoesNotExist:
        try:
            org = Organization.objects.get(id = org_id)
        except:
            return JsonResponse(
                {"success": False, "error": "Org not found"}, status=404
            ), False
        return JsonResponse(
            {"success": False, "error": "Not authorized to access page"}, status=403
        ), False


def check_project_auth(user_id: str, project_id: str):
    # Checks if user has access through proj->org link, returns True if the link exists
    try:
        project = Project.objects.get(id = project_id)
        logger.debug("Found Project, looking for org")
        return check_org_auth(user_id, project.org.id)
    except Project.DoesNotExist:
        return JsonResponse({"success": False, "error": "Project not found."}, status=404), False


def check_story_auth(user_id: str, story_id: str):
    # Checks if user has access through story->proj->org link, returns True if the link exists
    try:
        story = Story.objects.get(id = story_id)
        return check_project_auth(user_id, story.proj.id)
    except Story.DoesNotExist:
        return JsonResponse({"success": False, "error": "Story not found"}, status=404), False


def auth_level_check(user_level: str, required_level: str):
    """
    A way to check if a user can access a page.
    Exists pretty much entirely to allow for word inputs on access levels
    for readability purposes
    """
    auth_dict = {"creator": 3, "admin": 2, "user": 1, "visitor": 0}
    try:
        if auth_dict[user_level] >= auth_dict[required_level]:
            logger.debug(
            "Required Access Level: %r",
            auth_dict[required_level],
            )
            logger.debug(
                "Given Access Level: %r",
                auth_dict[user_level],
            )
            return True
        elif auth_dict[user_level] < auth_dict[required_level]:
            return JsonResponse(
                {"success": False, "error": "Insufficient Permissions"}, status=401
            )
    except:
        logger.debug(
            "Improperly Listed Permission Level?" "Required Access Level: %r",
            auth_dict[required_level],
        )
        logger.debug(
            "Given Access Level: %r",
            auth_dict[user_level],
        )
        return JsonResponse(
            {"success": False, "error": "Authorization Check Failed"}, status=401
        )


@require_GET
@csrf_exempt
def check_ml_status(request, story_id):
    """
    Input: story id
    Output: ML status, task type and timestamp of the story
    """
    try:
        ml_task = MLProcessingQueue.objects.get(story_id=story_id)
    except MLProcessingQueue.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "ML status not found"}, status=404
        )

    return JsonResponse(
        {
            "success": True,
            "task_type": ml_task.task_type,
            "timestamp": ml_task.timestamp,
            "ml_status": ml_task.status,
        },
        status=200,
    )


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
@verify_user('user')
def get_project(request, project_id):
    try:
        project = Project.objects.select_related("org", "curator").get(id=project_id)
        story_count = Story.objects.filter(proj=project).count()

        # Get associated ProjectTag objects
        project_tags = (
            ProjectTag.objects.filter(proj=project)
            .select_related("tag")  # Pull tag in same query
            .only("tag__name", "tag__required")
        )

        required_tags = []
        optional_tags = []

        for pt in project_tags:
            if pt.tag.required:
                required_tags.append(pt.tag.name)
            else:
                optional_tags.append(pt.tag.name)

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
@verify_user("user")
def get_org(request, org_id):
    try:
        org = get_object_or_404(Organization, id=org_id)

        # Get all projects and stories
        projects = Project.objects.filter(org=org).only("id", "curator")
        stories = Story.objects.filter(proj__in=projects).only("id", "curator")

        project_count = projects.count()
        story_count = stories.count()
        project_ids = list(projects.values_list("id", flat=True))

        # Collect unique curator IDs
        project_curator_ids = projects.values_list("curator", flat=True)
        story_curator_ids = stories.values_list("curator", flat=True)
        user_ids = set(project_curator_ids) | set(story_curator_ids)

        users = CustomUser.objects.filter(id__in=user_ids).values(
            "id", "name", "email", "position"
        )
        users_data = list(users)
        
        # Query OrgUser table for access levels
        org_user_access = OrgUser.objects.filter(
            org_id=org.id, user_id__in=user_ids
        ).values("user_id", "access")

        orguser_map = {entry["user_id"]: entry["access"] for entry in org_user_access}

        # Add access level to each user
        for user in users_data:
            user["access"] = orguser_map.get(user["id"])

        # Generate presigned URL
        profile_pic_url = ""
        if org.profile:
            presign = generate_s3_presigned(
                bucket_name=settings.CT_BUCKET_ORG_PROFILES,
                key=org.profile.name,
                operation="download",
                expiration=3600,
            )
            profile_pic_url = presign["url"]

        return JsonResponse(
            {
                "org_id": org.id,
                "name": org.name,
                "description": org.description,
                "profile_pic_path": profile_pic_url,
                "project_count": project_count,
                "project_ids": project_ids,
                "story_count": story_count,
                "users": users_data,
            },
            status=200,
        )

    except Exception as e:
        logging.error(f"Error in get_org: {e}")
        return JsonResponse({"error": "Something went wrong."}, status=500)


@require_GET
def get_stories(request):

    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        # Existing filter logic remains the same
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

        # Existing filtering logic remains the same
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

        # Optimize tag fetching
        stories = stories.select_related("proj", "curator").prefetch_related(
            Prefetch(
                "storytag_set",
                queryset=StoryTag.objects.select_related("tag"),
                to_attr="prefetched_story_tags",
            )
        )

        # Prepare the output with presigned URLs
        stories_data = []
        for story in stories.select_related("proj", "curator"):
            tag_list = [
                {
                    "name": st.tag.name,
                    "value": st.tag.value,
                    "created_by": st.tag.created_by,
                }
                for st in getattr(story, "prefetched_story_tags", [])
                if st.tag  # ensure tag exists
            ]
            stories_data.append(
                {
                    "story_id": story.id,
                    "storyteller": story.storyteller,
                    "project_id": story.proj.id,
                    "project_name": story.proj.name,
                    "curator": story.curator.name if story.curator else None,
                    "date": str(story.date),
                    "summary": story.summary,
                    "text_content": story.text_content,
                    "tags": tag_list,
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
@verify_user('user')
@cache_page(60 * 15)  # Cache for 15 minutes
def get_story(request, story_id):
    print(request.headers)

    try:
        story = Story.objects.select_related("proj", "curator").get(id=story_id)
        story_tags = StoryTag.objects.filter(story=story).select_related("tag")

        tags = [{"name": st.tag.name, "value": st.tag.value} for st in story_tags]

        audio_url = ""
        if story.audio_content:
            audio_presign = generate_s3_presigned(
                bucket_name=settings.CT_BUCKET_STORY_AUDIO,
                key=story.audio_content.name,
                operation="download",
                expiration=3600,
            )
            audio_url = audio_presign["url"] if audio_presign else ""

        image_url = ""
        if story.image_content:
            image_presign = generate_s3_presigned(
                bucket_name=settings.CT_BUCKET_STORY_IMAGES,
                key=story.image_content.name,
                operation="download",
                expiration=3600,
            )
            image_url = image_presign["url"] if image_presign else ""

        return JsonResponse(
            {
                "story_id": story.id,
                "project_id": story.proj.id,
                "project_name": story.proj.name,
                "storyteller": story.storyteller,
                "curator": story.curator.id if story.curator else None,
                "date": story.date,
                "text_content": story.text_content,
                "summary": story.summary,
                "tags": tags,
                "audio_path": audio_url,
                "image_path": image_url,
            },
            status=200,
        )

    except Story.DoesNotExist:
        logging.debug("Story not found with ID: %s", story_id)
        return HttpResponseNotFound(
            "Could not find that story. It may have been deleted or never existed.",
            status=404,
        )


## POST methods ----------------------------------------------------------------


@csrf_exempt
@require_http_methods(["POST", "GET", "OPTIONS"])
@verify_user("user")
def create_story(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    if request.method == "GET":
        try:
            user_id = request.user_id
            if not user_id:
                return JsonResponse(
                    {"success": False, "error": "Missing user_id"}, status=400
                )

            file_uuid = str(uuid4())
            audio_key = f"{user_id}/{file_uuid}"
            image_key = f"{user_id}/{file_uuid}"

            audio_presign = generate_s3_presigned(
                bucket_name=settings.CT_BUCKET_STORY_AUDIO,
                key=audio_key,
                operation="upload",
                expiration=3600,
                content_type="audio/mpeg",
            )

            image_presign = generate_s3_presigned(
                bucket_name=settings.CT_BUCKET_STORY_IMAGES,
                key=image_key,
                operation="upload",
                expiration=3600,
                content_type="image/png",
            )

            return JsonResponse(
                {
                    "success": True,
                    "audio_upload": {
                        "url": audio_presign["url"],
                        "fields": audio_presign.get("fields", {}),
                    },
                    "image_upload": {
                        "url": image_presign["url"],
                        "fields": image_presign.get("fields", {}),
                    },
                }
            )

        except Exception as e:
            logger.error("Error generating upload URLs: %s", str(e))
            return JsonResponse(
                {"success": False, "error": "Failed to generate upload URLs"},
                status=500,
            )

    try:
        logger.debug("Received request body: %s", request.body)
        story_data = json.loads(request.body)
        logger.debug("Parsed story data: %s", story_data)

        try:
            project = Project.objects.get(id=story_data["project_id"])
            logger.debug("Found project: %s", project)
        except Project.DoesNotExist:
            logger.error("Project with ID %s does not exist", story_data["project_id"])

            return JsonResponse(
                {"error": f"Project with ID {story_data["project_id"]} does not exist"},
                status=400,
            )

        logger.debug("Curator ID: %s", story_data.get("curator"))

        try:
            story = Story.objects.create(
                storyteller=story_data.get("storyteller"),
                curator_id=request.user_id,
                date=timezone.now(),
                text_content=story_data.get("text_content"),
                proj=project,
                audio_content=story_data.get("audio_path"),
                image_content=story_data.get("image_path"),
            )
            logger.debug("Created story: %s", story)
        except Exception as e:
            logger.error("Error creating story: %s", str(e))
            raise

        try:
            with transaction.atomic():

                all_tags = [
                    (tag_data, True) for tag_data in story_data.get("required_tags", [])
                ] + [
                    (tag_data, False)
                    for tag_data in story_data.get("optional_tags", [])
                ]

                story_tags_to_create = []
                for tag_data, is_required in all_tags:
                    tag, created = Tag.objects.get_or_create(
                        name=tag_data["name"],
                        value=tag_data["value"],
                        required=is_required,
                    )
                    if created:
                        logger.debug(
                            "Created new tag: name=%s, value=%s, required=%s",
                            tag.name,
                            tag.value,
                            is_required,
                        )

                    story_tags_to_create.append(
                        StoryTag(story_id=story.id, tag_id=tag.id)
                    )

                if story_tags_to_create:
                    StoryTag.objects.bulk_create(story_tags_to_create)
                    logger.debug(
                        "Created %d story tag relationships for story %s",
                        len(story_tags_to_create),
                        story.id,
                    )

        except Exception as e:
            logger.error("Error creating tags for story %s: %s", story.id, str(e))
            story.delete()
            raise

        producer = QueueProducer()
        queue_result = producer.add_to_queue(story)

        if not queue_result["success"]:
            logger.error("Failed to queue ML tasks")
        else:
            logger.info("Successfully queued ML tasks for story %s", story.id)

        return JsonResponse({"story_id": story.id}, status=200)

    except Exception as e:
        logger.error("Error creating story: %s", str(e))
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
            city=user_data.get("city", ""),
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

    # add get user id
    return JsonResponse({"success": True, "user_id": user.id}, status=201)


@require_POST
@verify_user('creator')
def add_user_to_org(request, org_id, add_user_id):
    """
    Receives a request with user_id and org_id its body and registers new user
    user-org relationship in the login table of the db.
    # TODO: Update docstrings and specify exceptions
    """
    try:
        org_user_data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    if not org_user_data["user_id"]:
        return JsonResponse(
            {
                "success": False,
                "error": f"User ID is missing",
            }
        )

    try:
        OrgUser.objects.create(
            user_id=add_user_id,
            org_id=org_id,
            access=org_user_data["access"],
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"success": True}, status=201)


@require_http_methods(["DELETE"])
@verify_user('creator')
def delete_user_from_org(request, org_id, del_user_id):
    
    try:
        user_to_delete = OrgUser.objects.get(
            org_id=org_id, user_id=del_user_id
        )
        user_to_delete.delete()
        return JsonResponse({"success": True}, status=200)
    except:
        return JsonResponse(
            {"success": False, "error": "Deletion Unsuccessful"}, status=400
        )

###############################################################################


@require_http_methods(["POST", "PATCH"])
@verify_user('admin')
def edit_story(request, story_id):

    try:
        story_updates = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    try:
        story = Story.objects.get(id=story_id)
        logging.debug("story id: %r", story.id)
        curator = CustomUser.objects.get(id=story_updates.get("curator"))
        logging.debug("curator id: %r", curator.id)
    except:
        return JsonResponse(
            {"success": False, "error": "Story does not exist"}, status=404
        )

    try:
        story.storyteller = story_updates["storyteller"]
        story.curator = curator
        if "date" in story_updates:
            story.date = story_updates["date"]
        story.text_content = story_updates["text_content"]

        if "image_content" in story_updates:
            story.image_content = story_updates["image_content"]
        if "audio_content" in story_updates:
            story.audio_content = story_updates["audio_content"]

    except Exception as e:
        logger.debug("error:", e)
        return JsonResponse({"success": False, "error": "Data edit failed"}, status=400)
    try:
        story.save()
        return JsonResponse({"success": True}, status=200)
    except:
        return JsonResponse({"success": False, "error": "DB Update Failed"}, status=500)


@require_http_methods(["DELETE"])
@verify_user('admin')
def delete_story(request, story_id):
    try:
        org_to_delete = Story.objects.get(id=story_id)
        org_to_delete.delete()
        return JsonResponse({"success": True}, status=200)
    except:
        return JsonResponse(
            {"success": False, "error": "Deletion Unsuccessful"}, status=400
        )


###############################################################################
@csrf_exempt
@require_POST
@verify_user("admin")
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

    curator = CustomUser.objects.get(id = project_data["curator"])

    try:
        project = Project.objects.create(
            name = project_data["name"],
            description = project_data["description"],
            curator = curator,
            org = org,
            date= project_data.get("date", date.today()),
        )
        # move the tag loop inside the try
        required_tags = project_data.get("required_tags", [])
        optional_tags = project_data.get("optional_tags", [])

        for rtag in required_tags:
            tag = Tag.objects.create(name=rtag, required=True)
            ProjectTag.objects.create(
                tag = tag.id,
                proj = project.id,
            )
        for otag in optional_tags:
            tag = Tag.objects.create(name=otag, required=False)
            ProjectTag.objects.create(
                tag = tag.id,
                proj = project.id,
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


@require_http_methods(["POST", "PATCH"])
@verify_user('admin')
def edit_project(request, org_id, project_id):
    """
    POST /project/<org_id>/<project_id>/edit
    Body: JSON { "name": str, "curator": int, "date": "YYYY-MM-DD" }
    """
    # 1) parse JSON
    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    name = body.get("name")
    curator_id = body.get("curator")
    date_str = body.get("date")

    if not all([name, curator_id, date_str]):
        return JsonResponse(
            {"success": False, "error": "Missing required fields"}, status=400
        )

    # 2) fetch the Project
    try:
        project = Project.objects.get(pk=project_id, org_id=org_id)
    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found."}, status=404
        )

    # 3) assign new values
    project.name = name
    try:
        project.curator = CustomUser.objects.get(pk=curator_id)
    except CustomUser.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Curator not found."}, status=400
        )

    # parse & assign date
    try:
        project.date = datetime.date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return JsonResponse(
            {"success": False, "error": "Invalid date format"}, status=400
        )

    # 4) save
    project.save()
    return JsonResponse({"success": True}, status=200)


@require_http_methods(["DELETE"])
@verify_user('admin')
def delete_project(request, org_id, project_id):
    try:
        proj_to_delete = Project.objects.get(id=project_id)
        proj_to_delete.delete()
        return JsonResponse({"success": True}, status=200)
    except:
        return JsonResponse(
            {"success": False, "error": "Deletion Unsuccessful"}, status=400
        )


@csrf_exempt
@require_POST
@verify_user("user")
def create_org(request: HttpRequest) -> JsonResponse:
    """
    Handle requests for creating new organizations

    input:
        request (HTTP request)
            - name (str): organization's name provided by the user
            - description (str): organization's description provided by the user
            - profile (bool): indicates if the user provided a profile picture

    return (HTTP response)
        -  Response content
            - success (bool): indicates if the request was fulfilled
            - org_id (): organization's unique identifier
        - status (int): HTTP status code
    """

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JsonResponse({"success": False, "error": "No token"}, status=401)

        # Parse and validate input data
    logger.debug("Received request body: %s", request.body)

    org_data = json.loads(request.body)

    logger.debug("Parsed organization data: %s", org_data)
    name = org_data.get("name")
    description = org_data.get("description")

    logger.debug("Parsed organization name: %s,", name)
    logger.debug("Parsed organization desc: %s,", description)

    if not name:
        return JsonResponse(
            {"success": False, "error": "Organization name is required"},
            status=400,
        )
    if not description:
        return JsonResponse(
            {"success": False, "error": "Organization description is required"},
            status=400,
        )

    if Organization.objects.filter(name=name).exists():
        logger.debug(
            "Organization already exists: %s",
            Organization.objects.filter(name=name).first(),
        )
        logger.debug("Organization with name %s already exists", name)
        return JsonResponse(
            {"success": False, "error": "Organization already exists"}, status=400
        )

    try:
        org = Organization.objects.create(
            name=name,
            description=description,
        )

        user = get_user_model().objects.get(pk=request.user_id)

        OrgUser.objects.create(org=org, user=user, access="admin")

    except KeyError as e:
        logger.error("KeyError: %s", str(e))
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"internal service error{str(e)}"}, status=500
        )

    return JsonResponse(
        {
            "success": True,
            "org_id": org.id,
        },
        status=201,
    )


@require_http_methods(["POST", "PATCH"])
@verify_user('admin')
def edit_org(request, org_id):

    try:
        org_updates = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    try:
        org = Organization.objects.get(id=org_id)
    except:
        return JsonResponse(
            {"success": False, "error": "Organization does not exist"}, status=404
        )

    try:
        org.name = (org_updates["name"],)
        org.description = org_updates["description"]
        org.save()
        return JsonResponse({"success": True}, status=200)
    except:
        return JsonResponse({"success": False, "error": "DB Update Failed"}, status=500)


@require_http_methods(["DELETE"])
@verify_user('creator')
def delete_org(request, org_id):
    try:
        org_to_delete = Organization.objects.get(id=org_id)
        org_to_delete.delete()
        return JsonResponse({"success": True}, status=200)
    except:
        return JsonResponse(
            {"success": False, "error": "Deletion Unsuccessful"}, status=400
        )


## User methods ----------------------------------------------------------------


@require_GET
@verify_user('user')
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
        user = User.objects.get(pk=user_id)

        # Generate presigned URL for user profile picture
        user_profile_url = ""
        if user.profile:
            user_presign = generate_s3_presigned(
                bucket_name=settings.CT_BUCKET_USER_PROFILES,
                key=user.profile.name,
                operation="download",
                expiration=3600,
            )
            user_profile_url = user_presign["url"]

        # Get organizations with presigned URLs for their profiles
        org_users = OrgUser.objects.filter(user=user).select_related("org")
        orgs = []
        for org_user in org_users:
            org = org_user.org
            org_profile_url = ""
            if org.profile:
                org_presign = generate_s3_presigned(
                    bucket_name=settings.CT_BUCKET_ORG_PROFILES,
                    key=org.profile.name,
                    operation="download",
                    expiration=3600,
                )
                org_profile_url = org_presign["url"]

            orgs.append(
                {
                    "org_id": str(org.id),
                    "org_name": org.name,
                    "org_profile_pic_path": org_profile_url,
                }
            )

        user_data = {
            "user_id": user.id,
            "name": user.name,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "city": user.city,
            "bio": user.bio,
            "position": user.position,
            "profile_pic_path": user_profile_url,
            "orgs": orgs,
        }

        return JsonResponse(user_data, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST", "PATCH"])
@verify_user('user')
def edit_user(request, user_id, **kwargs):

    try:
        user_updates = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    username = user_updates.get("username")
    if User.objects.filter(username=username).exists():
        return JsonResponse(
            {"success": False, "error": "Username already exists"}, status=400
        )

    user = CustomUser.objects.get(id=user_id)  # kwargs['real_user_id']

    try:
        user.username = (username,)
        user.password = (user_updates.get("password", ""),)
        user.first_name = (user_updates.get("first_name", ""),)
        user.last_name = (user_updates.get("last_name", ""),)
        user.email = (user_updates.get("email", ""),)
        user.name = (user_updates.get("name", ""),)
        user.save()
        return JsonResponse({"success": True}, status=200)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["DELETE"])
@verify_user()
def delete_user(request, user_id):

    try:
        user_to_delete = CustomUser.objects.get(id=request.user_id)  # kwargs['real_user_id']
        user_to_delete.delete()
        return JsonResponse({"success": True}, status=200)
    except:
        return JsonResponse(
            {"success": False, "error": "Deletion Unsuccessful"}, status=400
        )


## Org methods -----------------------------------------------------------------


# @verify_user
def get_org_projects(request, org_id):
    try:
        org = get_object_or_404(Organization, id=org_id)

        # Get all projects in the org
        projects = Project.objects.filter(org=org)
        project_count = projects.count()

        for project in projects:
            story_count = Story.objects.filter(proj=project).count()

        response_data = {
            "org_id": org.id,
            "name": org.name,
            "description": org.description,
            "profile_pic_path": org.profile.url if org.profile else "",
            "project_count": project_count,
            "projects": [
                {
                    "project_id": project.id,
                    "project_name": project.name,
                    "story_count": story_count,
                }
                for project in projects
            ],
        }

        return JsonResponse(response_data, status=200)

    except Exception as e:
        logging.error(f"Error in get_org: {e}")
        return JsonResponse({"error": "Something went wrong."}, status=500)


# EOF. ------------------------------------------------------------------------
