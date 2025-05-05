from django.http import HttpResponse, HttpResponseNotFound
# the names of the models may change on a different branch.


# Create your views here.

def home_test(request):
    return HttpResponse("Welcome to the Common Threads Home Page!", status=200)

def show_org_dashboard(request, user_id, org_id):
    if user_id is None or org_id is None:
        return HttpResponseNotFound("User ID or Organization ID not provided.")
    # empty for now
    return HttpResponse(f"Organization Dashboard for ID: {org_id}", status=200)

def show_project_dashboard(request, user_id, org_id, project_id):
    if user_id is None or org_id is None or project_id is None:
        return HttpResponseNotFound("User ID, Organization ID, or Project ID not provided.")
    # empty for now
    return HttpResponse(f"Project Dashboard for ID: {project_id}", status=200)