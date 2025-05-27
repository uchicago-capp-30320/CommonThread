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
    create_error_response,
    find_user_by_email,
    AUTH_ERRORS,
    RESOURCE_ERRORS,
    VALIDATION_ERRORS,
    BUSINESS_ERRORS,
    SERVER_ERRORS,
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
from botocore.exceptions import ClientError, ParamValidationError

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
                    return create_error_response("NO_TOKEN", AUTH_ERRORS)
                elif not access_token.startswith("Bearer "):
                    return create_error_response("INVALID_TOKEN", AUTH_ERRORS)
                access_token = access_token.split(" ", 1)[1]
                decoded = decode_access_token(access_token)
                real_user_id = decoded["sub"]

            except ExpiredSignatureError:
                # Expired Token: 299 Code used by front-end to know to request new one
                return create_error_response("ACCESS_TOKEN_EXPIRED", AUTH_ERRORS)
            except InvalidTokenError:
                # Something broke in the process
                return create_error_response("INVALID_TOKEN", AUTH_ERRORS)

            request.user_id = decoded["sub"]
            # Identifying what kind of request/auth level the user has for their request
            if kwargs:
                logging.debug("Kwargs used in Auth")
                auth_level, search_success = id_searcher(
                    real_user_id, kwargs, required_access
                )
            else:
                logging.debug("Request used in Auth")
                try:
                    body = json.loads((request.body or "{}"))
                except:
                    logging.debug("Request failed to load")
                    return create_error_response("INVALID_JSON", VALIDATION_ERRORS)
                auth_level, search_success = id_searcher(
                    real_user_id, body, required_access
                )
            logger.debug("Test Checking")
            logger.debug(auth_level)
            logger.debug(search_success)
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
            # If there's a user id in there but we need admin/creator for some purpose.
            # This essentially serves as a failsafe against things that might include user ids
            if "org_id" not in id_set:
                if "project_id" not in id_set:
                    if "story_id" not in id_set:
                        return (
                            create_error_response("BAD_FILTER", RESOURCE_ERRORS),
                            False,
                        )
                    else:
                        return check_story_auth(real_user_id, id_set["story_id"])
                else:
                    return check_project_auth(real_user_id, id_set["project_id"])
            else:
                return check_org_auth(real_user_id, id_set["org_id"])
        else:
            return "user", True

    except:
        return create_error_response("INVALID_JSON", VALIDATION_ERRORS), False


def check_org_auth(user_id: str, org_id: str):
    # Checks if user has access to an organization, returns True if the link exists
    try:
        row = OrgUser.objects.get(user_id=user_id, org_id=org_id)
        return row.access, True
    except OrgUser.DoesNotExist:
        try:
            org = Organization.objects.get(id=org_id)
        except:
            return create_error_response("ORG_NOT_FOUND", RESOURCE_ERRORS), False
        return create_error_response("USER_NOT_IN_ORG", AUTH_ERRORS), False


def check_project_auth(user_id: str, project_id: str):
    # Checks if user has access through proj->org link, returns True if the link exists
    try:
        project = Project.objects.get(id=project_id)
        logger.debug("Found Project, looking for org")
        return check_org_auth(user_id, project.org.id)
    except Project.DoesNotExist:
        return create_error_response("PROJECT_NOT_FOUND", RESOURCE_ERRORS), False


def check_story_auth(user_id: str, story_id: str):
    # Checks if user has access through story->proj->org link, returns True if the link exists
    try:
        story = Story.objects.get(id=story_id)
        return check_project_auth(user_id, story.proj.id)
    except Story.DoesNotExist:
        return create_error_response("STORY_NOT_FOUND", RESOURCE_ERRORS), False


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
            return create_error_response("INSUFFICIENT_PERMISSIONS", AUTH_ERRORS), False
    except:
        logger.debug(
            "Improperly Listed Permission Level?" "Required Access Level: %r",
            auth_dict[required_level],
        )
        logger.debug(
            "Given Access Level: %r",
            auth_dict[user_level],
        )
        return create_error_response("INVALID_CREDENTIALS", AUTH_ERRORS), False


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
        return create_error_response("STORY_NOT_FOUND", RESOURCE_ERRORS)

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
        except json.JSONDecodeError as e:
            logger.debug("LOGIN ➤ JSON parse failed: %r", e)
            return create_error_response("INVALID_JSON", VALIDATION_ERRORS)
    else:
        data = request.POST
        logger.debug("LOGIN ➤ form-data: %r", data)

    username = data.get("username")
    password = data.get("password")

    logger.debug("LOGIN ➤ extracted username=%r password=%r", username, password)

    if not username or not password:
        return create_error_response("INVALID_CREDENTIALS", AUTH_ERRORS)

    authenticated_user = authenticate(username=username, password=password)
    logger.debug("LOGIN ➤ authenticate returned %r", authenticated_user)

    if authenticated_user is None:
        return create_error_response("INVALID_CREDENTIALS", AUTH_ERRORS)

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
    logger.debug("REFRESH: content-type=%r body=%r", request.content_type, request.body)

    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            logger.debug("REFRESH: token JSON parse failed")
            return create_error_response("INVALID_JSON", VALIDATION_ERRORS)
    else:
        data = request.POST
        logger.debug("REFRESH: form-data: %r", data)

    refresh_token = data.get("refresh_token")
    logger.debug("REFRESH: got refresh_token=%r", refresh_token)
    if not refresh_token:
        return create_error_response("NO_TOKEN", AUTH_ERRORS)

    try:
        decoded_refresh = decode_refresh_token(refresh_token)
        logger.debug("REFRESH: decoded payload: %r", decoded_refresh)
        user_id = decoded_refresh.get("sub")
        new_access_token = generate_access_token(user_id)
        return JsonResponse({"success": True, "access_token": new_access_token})
    except ExpiredSignatureError:
        # we need to redirect to login? Onur says we can't do this, frontend should handle it
        logger.debug("REFRESH: expired")
        return create_error_response("REFRESH_TOKEN_EXPIRED", AUTH_ERRORS)
    except InvalidTokenError:
        logger.debug("REFRESH: invalid")
        return create_error_response("INVALID_TOKEN", AUTH_ERRORS)
    except Exception:
        return create_error_response("INTERNAL_ERROR", SERVER_ERRORS)


@require_GET
@verify_user("user")
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
            "insight": project.insight_json,
            "curator": project.curator.name if project.curator else None,
            "required_tags": list(required_tags),
            "optional_tags": list(optional_tags),
            "stories": story_count,
        }

        return JsonResponse(data)

    except Project.DoesNotExist:
        logger.warning(f"Project with id={project_id} not found.")
        return create_error_response("PROJECT_NOT_FOUND", RESOURCE_ERRORS)

    except Exception as e:
        logger.error(f"Error in get_project: {e}", exc_info=True)
        return create_error_response("INTERNAL_ERROR", SERVER_ERRORS)


@require_GET
@verify_user("user")
def get_org(request, org_id):
    try:
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return create_error_response("ORG_NOT_FOUND", RESOURCE_ERRORS)

        # Get all projects and stories
        projects = Project.objects.filter(org=org).only("id", "curator")
        stories = Story.objects.filter(proj__in=projects).only("id", "curator")

        project_count = projects.count()
        story_count = stories.count()
        project_ids = list(projects.values_list("id", flat=True))

        # get all users from OrgUser table
        org_users = OrgUser.objects.filter(org=org).values_list("user_id", flat=True)

        users = CustomUser.objects.filter(id__in=org_users).values(
            "id", "name", "email", "position"
        )
        users_data = list(users)

        # Query OrgUser table for access levels
        org_user_access = OrgUser.objects.filter(
            org_id=org.id, user_id__in=org_users
        ).values("user_id", "access")

        orguser_map = {entry["user_id"]: entry["access"] for entry in org_user_access}

        # Add access level to each user
        for user in users_data:
            user["access"] = orguser_map.get(user["id"])

        # Generate presigned URL
        profile_pic_url = ""
        if org.profile:
            try:
                presign = generate_s3_presigned(
                    bucket_name=settings.CT_BUCKET_ORG_PROFILES,
                    key=org.profile.name,
                    operation="download",
                    expiration=3600,
                )
                profile_pic_url = presign["url"]
            except ClientError as e:
                logger.error(f"Failed to generate S3 URL: {e}", exc_info=True)
                return create_error_response("S3_ERROR", SERVER_ERRORS)

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
        logger.error(f"Unhandled error in get_org: {e}", exc_info=True)
        return create_error_response("INTERNAL_ERROR", SERVER_ERRORS)


@require_GET
@verify_user("user")
def get_stories(request):

    try:
        # Existing filter logic remains the same
        org_id = request.GET.get("org_id")
        project_id = request.GET.get("project_id")
        story_id = request.GET.get("story_id")
        user_id = request.GET.get("user_id")

    except KeyError as e:
        logger.error(f"Error in get_stories: {e}")
        return create_error_response("MISSING_REQUIRED_FIELDS", VALIDATION_ERRORS)

    filters = {
        "org_id": org_id,
        "project_id": project_id,
        "story_id": story_id,
        "user_id": user_id,
    }
    active_filter = {k: v for k, v in filters.items() if v is not None}

    if len(active_filter) != 1:
        return create_error_response("BAD_FILTER", RESOURCE_ERRORS)

    id_type, id_value = next(iter(active_filter.items()))

    if id_type == "org_id":
        stories = Story.objects.filter(proj__org__id=id_value)

    elif id_type == "project_id":
        stories = Story.objects.filter(proj__id=id_value)

    elif id_type == "story_id":
        stories = Story.objects.filter(id=id_value)

    elif id_type == "user_id":
        stories = Story.objects.filter(curator__id=id_value)

    else:
        return create_error_response("INVALID_QUERY_PARAM", RESOURCE_ERRORS)

    try:
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
        return create_error_response("INTERNAL_ERROR", SERVER_ERRORS)


@require_GET
@verify_user("user")
@cache_page(60 * 15)  # Cache for 15 minutes
def get_story(request, story_id):
    print(request.headers)

    try:
        story = Story.objects.select_related("proj", "curator").get(id=story_id)
        story_tags = StoryTag.objects.filter(story=story).select_related("tag")

        tags = [
            {
                "name": st.tag.name,
                "value": st.tag.value,
                "created_by": st.tag.created_by,
            }
            for st in story_tags
        ]

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
        return create_error_response("STORY_NOT_FOUND", RESOURCE_ERRORS)


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
                return create_error_response(
                    "MISSING_REQUIRED_FIELDS",
                    VALIDATION_ERRORS,
                    {"missing_field": "user_id"},
                )

            file_uuid = str(uuid4())
            audio_key = f"{user_id}/{file_uuid}"
            image_key = f"{user_id}/{file_uuid}"

            try:
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
            except Exception as e:
                logger.error("S3 presigned URL generation failed: %s", str(e))
                return create_error_response("S3_ERROR", SERVER_ERRORS)

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
            logger.error("Error in GET handling: %s", str(e))
            return create_error_response("INTERNAL_ERROR", SERVER_ERRORS)

    # POST handling
    try:
        logger.debug("Received request body: %s", request.body)
        try:
            story_data = json.loads(request.body)
            logger.debug("Parsed story data: %s", story_data)
        except json.JSONDecodeError:
            return create_error_response("INVALID_JSON", VALIDATION_ERRORS)

        try:
            project = Project.objects.get(id=story_data["project_id"])
            logger.debug("Found project: %s", project)
        except Project.DoesNotExist:
            logger.error("Project with ID %s does not exist", story_data["project_id"])
            return create_error_response(
                "PROJECT_NOT_FOUND",
                RESOURCE_ERRORS,
                {"project_id": story_data["project_id"]},
            )
        except KeyError:
            return create_error_response(
                "MISSING_REQUIRED_FIELDS",
                VALIDATION_ERRORS,
                {"missing_field": "project_id"},
            )

        logger.debug("Curator ID: %s", story_data.get("curator"))

        with transaction.atomic():
            try:
                # Create the story
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

                # Handle tags
                all_tags = [
                    (tag_data, True) for tag_data in story_data.get("required_tags", [])
                ] + [
                    (tag_data, False)
                    for tag_data in story_data.get("optional_tags", [])
                ]

                story_tags_to_create = []
                for tag_data, is_required in all_tags:
                    if (
                        not isinstance(tag_data, dict)
                        or "name" not in tag_data
                        or "value" not in tag_data
                    ):
                        logger.warning("Invalid tag format: %s", tag_data)
                        continue

                    try:
                        tag, created = Tag.objects.get_or_create(
                            name=tag_data["name"],
                            value=tag_data["value"],
                            created_by="user",
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
                    except Exception as e:
                        logger.warning("Failed to create tag %s: %s", tag_data, str(e))

                if story_tags_to_create:
                    StoryTag.objects.bulk_create(story_tags_to_create)
                    logger.debug(
                        "Created %d story tag relationships for story %s",
                        len(story_tags_to_create),
                        story.id,
                    )

            except ValueError as _:
                return create_error_response("INVALID_TAG_FORMAT", VALIDATION_ERRORS)
            except Exception as e:
                logger.error("Database operation failed: %s", str(e))
                return create_error_response("DATABASE_ERROR", SERVER_ERRORS)

        # Queue ML processing
        # For now, we are not giving back error for ML queue failure to the client
        # They can use the ml_status endpoint to check the status of the ML processing
        try:
            producer = QueueProducer()
            queue_result = producer.add_to_queue(story)

            if not queue_result["success"]:
                logger.error("Failed to queue ML tasks")
                # return create_error_response('ML_QUEUE_FAILED', BUSINESS_ERRORS)

            logger.info("Successfully queued ML tasks for story %s", story.id)
        except Exception as e:
            logger.error("Queue service error: %s", str(e))
            # return create_error_response('QUEUE_SERVICE_ERROR', SERVER_ERRORS)

        return JsonResponse({"success": True, "story_id": story.id}, status=200)

    except Exception as e:
        logger.error("Unhandled error in create_story: %s", str(e))
        return create_error_response("INTERNAL_ERROR", SERVER_ERRORS)


@csrf_exempt
@require_POST
@transaction.atomic
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
        return create_error_response("INVALID_JSON", VALIDATION_ERRORS)

    username = user_data.get("username")
    password = user_data.get("password")
    if not username or not password:
        return create_error_response("MISSING_REQUIRED_FIELDS", VALIDATION_ERRORS)

    #  check for existing user
    if User.objects.filter(username=username).exists():
        return create_error_response("DUPLICATE_USERNAME", BUSINESS_ERRORS)

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
    except Exception:
        return create_error_response("INTERNAL_ERROR", SERVER_ERRORS)

    # add get user id
    return JsonResponse({"success": True, "user_id": user.id}, status=201)


@csrf_exempt
@require_POST
@transaction.atomic
@verify_user("creator")
def add_user_to_org(request, org_id):
    """
    Receives a request with user_id and org_id its body and registers new user
    user-org relationship in the login table of the db.
    # TODO: Update docstrings and specify exceptions
    """

    try:
        logger.debug("Received request body: %s", request.body)

        try:
            org_user_data = json.loads(request.body or "{}")
            logger.debug("Parsed org user data: %s", org_user_data)

        except json.JSONDecodeError:
            return create_error_response("INVALID_JSON", VALIDATION_ERRORS)

        try:
            user = find_user_by_email(org_user_data["email"], CustomUser)
            logger.debug("Found user: %s", user)

            if OrgUser.objects.filter(user_id=user.id, org_id=org_id).exists():
                return create_error_response("USER_ALREADY_IN_ORG", BUSINESS_ERRORS)

            try:
                orguser = OrgUser.objects.create(
                    user_id=user.id, org_id=org_id, access=org_user_data["access"]
                )
                logger.debug("Created OrgUser relationship %s", orguser)

            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)}, status=400)

        except user.DoesNotExist:
            logger.error("User with email %s does not exist", org_user_data["email"])
            return create_error_response(
                "USER_NOT_FOUND",
                RESOURCE_ERRORS,
                {"add_user_id": org_user_data["add_user_id"]},
            )

        except KeyError:
            return create_error_response(
                "MISSING_REQUIRED_FIELDS",
                VALIDATION_ERRORS,
                {"missing_field": "email"},
            )
        except Exception as e:
            logger.warning("Failed to add user %s: %s", user.id, str(e))
            return create_error_response("INTERNAL_ERROR", SERVER_ERRORS)

        return JsonResponse({"success": True, "orguser_id": orguser.id}, status=200)

    except Exception as e:
        logger.exception("Unexpected error in add_user_to_org: %s", str(e))
        return create_error_response("UNEXPECTED_ERROR", SERVER_ERRORS)


@csrf_exempt
@require_http_methods(["DELETE"])
@verify_user("creator")
def delete_user_from_org(request, org_id, del_user_id):

    # check if user already is not in org
    if not OrgUser.objects.filter(user_id=del_user_id, org_id=org_id).exists():
        return create_error_response("USER_NOT_IN_ORG", BUSINESS_ERRORS)

    try:
        user_to_delete = OrgUser.objects.get(org_id=org_id, user_id=del_user_id)
        user_to_delete.delete()
        return JsonResponse({"success": True}, status=200)
    except:
        return create_error_response("DATABASE_ERROR", SERVER_ERRORS)


###############################################################################


@require_http_methods(["POST", "PATCH"])
@verify_user("admin")
def edit_story(request, story_id):

    try:
        story_updates = json.loads(request.body)
    except json.JSONDecodeError:
        return create_error_response("INVALID_JSON", VALIDATION_ERRORS)

    try:
        story = Story.objects.get(id=story_id)
        logging.debug("story id: %r", story.id)
        curator = CustomUser.objects.get(id=story_updates.get("curator"))
        logging.debug("curator id: %r", curator.id)
    except:
        return create_error_response("STORY_NOT_FOUND", RESOURCE_ERRORS)

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
        return create_error_response("DATABASE_ERROR", SERVER_ERRORS)
    try:
        story.save()
        return JsonResponse({"success": True}, status=200)
    except:
        return create_error_response("DATABASE_ERROR", SERVER_ERRORS)


@csrf_exempt
@require_http_methods(["DELETE"])
@verify_user("admin")
def delete_story(request, story_id):
    try:
        org_to_delete = Story.objects.get(id=story_id)
        org_to_delete.delete()
        return JsonResponse({"success": True}, status=200)
    except:
        return create_error_response("DATABASE_ERROR", SERVER_ERRORS)


###############################################################################
@csrf_exempt
@require_POST
@transaction.atomic
@verify_user("admin")
def create_project(request):
    try:
        logger.debug("Received request body: %s", request.body)
        project_data = json.loads(request.body or "{}")
        logger.debug("Parsed project data: %s", project_data)
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
        logger.debug("Found organization: %s", org)
    except Organization.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Organization not found"}, status=404
        )

    curator = CustomUser.objects.get(id=request.user_id)
    logger.debug("Curator ID: %s", curator)

    try:
        logger.debug("Creating project with data: %s", project_data)
        project = Project.objects.create(
            name=project_data["project_name"],
            description=project_data["description"],
            curator=curator,
            org=org,
            date=str(date.today()),
        )
        # move the tag loop inside the try
        required_tags = project_data.get("required_tags", [])
        optional_tags = project_data.get("optional_tags", [])

        logger.debug("Creating tags for project %s", project.id)
        logger.debug("Required tags: %s", required_tags)
        logger.debug("Optional tags: %s", optional_tags)
        for rtag in required_tags:
            tag = Tag.objects.create(name=rtag, required=True)
            ProjectTag.objects.create(
                tag=tag,
                proj=project,
            )
        for otag in optional_tags:
            tag = Tag.objects.create(name=otag, required=False)
            ProjectTag.objects.create(
                tag=tag,
                proj=project,
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
@verify_user("admin")
def edit_project(request, project_id):
    """
    POST /project/<org_id>/<project_id>/edit
    Body: JSON { "name": str, "curator": int, "date": "YYYY-MM-DD" }
    """
    # 1) parse JSON
    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return create_error_response("INVALID_JSON", VALIDATION_ERRORS)

    name = body.get("name")
    curator_id = body.get("curator")
    date_str = body.get("date")
    org_id = body.get("org_id")

    if not all([name, curator_id, date_str]):
        return create_error_response("MISSING_REQUIRED_FIELDS", VALIDATION_ERRORS)

    # 2) fetch the Project
    try:
        project = Project.objects.get(pk=project_id, org_id=org_id)
    except Project.DoesNotExist:
        return create_error_response("PROJECT_NOT_FOUND", RESOURCE_ERRORS)

    # 3) assign new values
    project.name = name
    try:
        project.curator = CustomUser.objects.get(pk=curator_id)
    except CustomUser.DoesNotExist:
        return create_error_response(
            "USER_NOT_FOUND", RESOURCE_ERRORS, "Curator not in Users"
        )

    # parse & assign date
    try:
        project.date = datetime.date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return create_error_response("INVALID_DATE_FORMAT", VALIDATION_ERRORS)

    # 4) save
    try:
        project.save()
        return JsonResponse({"success": True}, status=200)
    except:
        return create_error_response("DATABASE_ERROR", SERVER_ERRORS)


@csrf_exempt
@require_http_methods(["DELETE"])
@verify_user("admin")
def delete_project(request, project_id):
    try:
        proj_to_delete = Project.objects.get(id=project_id)

        proj_to_delete.delete()
        return JsonResponse({"success": True}, status=200)
    except:
        return create_error_response("DATABASE_ERROR", SERVER_ERRORS)


@csrf_exempt
@require_POST
@transaction.atomic
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
        return create_error_response("NO_TOKEN", AUTH_ERRORS)

    # Parse and validate input data
    logger.debug("Received request body: %s", request.body)

    org_data = json.loads(request.body)

    logger.debug("Parsed organization data: %s", org_data)
    name = org_data.get("name")
    description = org_data.get("description")

    logger.debug("Parsed organization name: %s,", name)
    logger.debug("Parsed organization desc: %s,", description)

    if not name:
        return create_error_response("MISSING_REQUIRED_FIELDS", VALIDATION_ERRORS)

    if not description:
        return create_error_response("MISSING_REQUIRED_FIELDS", VALIDATION_ERRORS)

    if Organization.objects.filter(name=name).exists():
        logger.debug(
            "Organization already exists: %s",
            Organization.objects.filter(name=name).first(),
        )
        logger.debug("Organization with name %s already exists", name)
        return create_error_response("DUPLICATE_ORG_NAME", BUSINESS_ERRORS)

    try:
        org = Organization.objects.create(description=description, name=name)

        user = get_user_model().objects.get(pk=request.user_id)

        OrgUser.objects.create(org=org, user=user, access="admin")

    except KeyError as e:
        logger.error("KeyError: %s", str(e))
        return create_error_response("MISSING_REQUIRED_FIELDS", VALIDATION_ERRORS)
    except Exception as e:
        return create_error_response("INTERNAL_ERROR", SERVER_ERRORS)

    return JsonResponse(
        {
            "success": True,
            "org_id": org.id,
        },
        status=201,
    )


@require_http_methods(["POST", "PATCH"])
@verify_user("admin")
def edit_org(request, org_id):

    try:
        org_updates = json.loads(request.body)
    except json.JSONDecodeError:
        return create_error_response("INVALID_JSON", VALIDATION_ERRORS)

    try:
        org = Organization.objects.get(id=org_id)
    except:
        return create_error_response("ORG_NOT_FOUND", RESOURCE_ERRORS)

    try:
        org.name = (org_updates["name"],)
        org.description = org_updates["description"]
        org.save()
        return JsonResponse({"success": True}, status=200)
    except:
        return create_error_response("DATABASE_ERROR", SERVER_ERRORS)


@csrf_exempt
@require_http_methods(["DELETE"])
@verify_user("creator")
def delete_org(request, org_id):
    try:
        org_to_delete = Organization.objects.get(id=org_id)
        org_to_delete.delete()
        return JsonResponse({"success": True}, status=200)
    except:
        return create_error_response("DATABASE_ERROR", SERVER_ERRORS)


## User methods ----------------------------------------------------------------


@require_GET
@verify_user("user")
def get_user(request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return create_error_response("NO_TOKEN", AUTH_ERRORS)

    token = auth_header.split(" ", 1)[1]
    try:
        payload = decode_access_token(token)
        user_id = payload["sub"]
    except ExpiredSignatureError:
        return create_error_response("ACCESS_TOKEN_EXPIRED", AUTH_ERRORS)
    except InvalidTokenError:
        return create_error_response("INVALID_TOKEN", AUTH_ERRORS)

    try:
        user = User.objects.get(pk=user_id)

        # Generate presigned URL for user profile picture
        user_profile_url = ""
        if user.profile:
            try:
                user_presign = generate_s3_presigned(
                    bucket_name=settings.CT_BUCKET_USER_PROFILES,
                    key=user.profile.name,
                    operation="download",
                    expiration=3600,
                )
                user_profile_url = user_presign["url"]
            except Exception:
                return create_error_response("S3_ERROR", SERVER_ERRORS)

        # Get organizations with presigned URLs for their profiles
        org_users = OrgUser.objects.filter(user=user).select_related("org")
        orgs = []
        for org_user in org_users:
            org = org_user.org
            org_profile_url = ""
            if org.profile:
                try:
                    org_presign = generate_s3_presigned(
                        bucket_name=settings.CT_BUCKET_ORG_PROFILES,
                        key=org.profile.name,
                        operation="download",
                        expiration=3600,
                    )
                    org_profile_url = org_presign["url"]
                except Exception:
                    return create_error_response("S3_ERROR", SERVER_ERRORS)

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

    except User.DoesNotExist:
        return create_error_response("USER_NOT_FOUND", RESOURCE_ERRORS)
    except Exception:
        return create_error_response("INTERNAL_ERROR", SERVER_ERRORS)


@require_http_methods(["POST", "PATCH"])
@verify_user("user")
def edit_user(request, user_id, **kwargs):

    try:
        user_updates = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return create_error_response("INVALID_JSON", VALIDATION_ERRORS)

    username = user_updates.get("username")
    if User.objects.filter(username=username).exists():
        return create_error_response("DUPLICATE_USERNAME", BUSINESS_ERRORS)

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
        logger.debug(e)
        return create_error_response("DATABASE_ERROR", SERVER_ERRORS)


@csrf_exempt
@require_http_methods(["DELETE"])
@verify_user()
def delete_user(request, user_id):

    try:
        user_to_delete = CustomUser.objects.get(
            id=request.user_id
        )  # kwargs['real_user_id']
        user_to_delete.delete()
        return JsonResponse({"success": True}, status=200)
    except:
        return create_error_response("DATABASE_ERROR", SERVER_ERRORS)


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
