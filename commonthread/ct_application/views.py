import json
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseForbidden
from .models import User, Organization, OrgUser, Project, Story,Tag, ProjectTag # This is how we query data from the database 
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

###############################################################################
@require_GET
#TODO authentication and authorization check
def get_story(request,story_id = None):
    if story_id:
        try:
            story = Story.objects.get(story_id = story_id)
            return JsonResponse({
                "story_id": story.story_id,
                "story_teller": story.storyteller,
                "curator":story.curator,
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
                'stories': list(stories.values("story_id","story_teller","curator","date","content"))
            },status = 200)
        except Exception as e:
            return JsonResponse({"success": False, "error":str(e)}, status = 500)

###############################################################################
@require_POST
#TODO authentication and authorization check
def create_story(request):
    try:
        story_data = json.loads(request.body)
        _ = Story.objects.create(
                story_id =  story_data.get("story_id"),
                story_teller = story_data.get("storyteller"),
                curator = story_data.get("curator"),
                date =  story_data.get("date"),
                content =  story_data.get("content")
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

    project_data = json.loads(request.body)
    if not project_data:
        #second level validation
        return JsonResponse({"success":False, "error":"No project input"}, status = 400)

    org_id = project_data.get('org_id')
    if not org_id:
        return JsonResponse({
            "success": False,
            "error": 'Organization is required'
        }, status=400)
    
    try:
        project = Project.objects.create(
            name=project_data['name'],
            curator=project_data['curator'],
            org_id=project_data['org_id'],
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

    #decide if atleast one tag is compulsory
    tags = project_data.get('tags', [])
    for tag_name in tags:

        tag= Tag.objects.create(name=tag_name)
        ProjectTag.objects.create(
            tag_id=tag.tag_id,
            proj_id=project.proj_id
        )

    return JsonResponse({
            'success': True,
            'project_id': project.id,
        }, status=201)
    
