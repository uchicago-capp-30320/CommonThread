# ct_application/tests/backend/test_endpoints.py

import json
import pytest
from django.test import Client
from ct_application.models import (
    CustomUser,
    Organization,
    OrgUser,
    Project,
    Story,
    Tag,
    StoryTag,
    ProjectTag,
    UserLogin,
)

pytestmark = pytest.mark.django_db  # enable database access for all tests in this module


@pytest.fixture
def setup_data():
    # Users
    alice = CustomUser.objects.create_user(
        username="alice", password="pass123", name="Alice Anderson", email="alice@uchicago.edu"
    )
    brenda = CustomUser.objects.create_user(
        username="brenda", password="secret456", name="Brenda Brown", email="brenda@uchicago.edu"
    )

    # Link to UserLogin
    UserLogin.objects.create(user_id=alice, username="alice", password="pass123")
    UserLogin.objects.create(user_id=brenda, username="brenda", password="secret456")

    # Organizations
    org1 = Organization.objects.create(name="University of Chicago")
    org2 = Organization.objects.create(name="Hyde Park Historical Society")
    org3 = Organization.objects.create(name="Chicago Story Guild")

    # OrgUser memberships
    OrgUser.objects.create(user_id=alice, org_id=org1, access="admin")
    OrgUser.objects.create(user_id=brenda, org_id=org2, access="admin")
    OrgUser.objects.create(user_id=alice, org_id=org3, access="admin")

    # Projects
    proj1 = Project.objects.create(
        org_id=org1, name="Campus Tales", curator=alice, date="2025-04-01"
    )
    proj2 = Project.objects.create(
        org_id=org2, name="Memory Lane", curator=brenda, date="2025-03-15"
    )

    # Stories
    story1 = Story.objects.create(
        proj_id=proj1,
        org_id=org1,
        storyteller="Alice A.",
        curator=alice,
        date="2025-04-05",
        content="Story one content",
    )
    story2 = Story.objects.create(
        proj_id=proj1,
        org_id=org1,
        storyteller="Bob B.",
        curator=brenda,
        date="2025-04-10",
        content="Story two content",
    )

    # Tags & link tables
    tag1 = Tag.objects.create(name="Fun")
    StoryTag.objects.create(story_id=story1, tag_id=tag1)
    ProjectTag.objects.create(proj_id=proj1, tag_id=tag1)

    return {
        "alice": alice,
        "brenda": brenda,
        "org1": org1,
        "org2": org2,
        "proj1": proj1,
        "proj2": proj2,
        "story1": story1,
        "story2": story2,
    }


@pytest.fixture
def client():
    return Client()


def test_home_test(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.content == b"Welcome to the Common Threads Home Page!"


def test_login_success(client, setup_data):
    alice = setup_data["alice"]
    body = json.dumps({"username": alice.username, "password": "pass123"})
    resp = client.post("/login", data=body, content_type="application/json")
    assert resp.status_code == 200


def test_login_forbidden(client, setup_data):
    alice = setup_data["alice"]
    body = json.dumps({"username": alice.username, "password": "wrongpassword"})
    resp = client.post("/login", data=body, content_type="application/json")
    assert resp.status_code == 403


def test_refresh_success(client, setup_data):
    alice = setup_data["alice"]
    # first log in to get refresh token
    login = client.post(
        "/login",
        data=json.dumps({"username": alice.username, "password": "pass123"}),
        content_type="application/json",
    )
    refresh_token = login.json()["refresh_token"]

    # now refresh
    refresh = client.post(
        "/login/create_access",
        data=json.dumps({"refresh_token": refresh_token}),
        content_type="application/json",
    )
    assert refresh.status_code == 200
    data = refresh.json()
    assert data["success"] is True
    assert "access_token" in data


def test_show_project_dashboard_success(client, setup_data):
    alice = setup_data["alice"]
    org1 = setup_data["org1"]
    proj1 = setup_data["proj1"]

    resp = client.get(f"/org/{alice.user_id}/{org1.org_id}/project/{proj1.proj_id}/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_id"] == proj1.proj_id
    assert data["story_count"] == 2
    assert data["tag_count"] == 1


def test_show_project_dashboard_forbidden(client, setup_data):
    brenda = setup_data["brenda"]
    org1 = setup_data["org1"]
    proj1 = setup_data["proj1"]

    resp = client.get(f"/org/{brenda.user_id}/{org1.org_id}/project/{proj1.proj_id}/")
    assert resp.status_code == 403


def test_show_org_dashboard_success(client, setup_data):
    alice = setup_data["alice"]
    org1 = setup_data["org1"]

    resp = client.get(f"/org/{alice.user_id}/{org1.org_id}/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["organization_id"] == org1.org_id
    assert data["project_count"] == 1


def test_show_org_dashboard_forbidden(client, setup_data):
    alice = setup_data["alice"]
    org2 = setup_data["org2"]

    resp = client.get(f"/org/{alice.user_id}/{org2.org_id}/")
    assert resp.status_code == 403


def test_get_story_list(client, setup_data):
    resp = client.get("/stories/")
    assert resp.status_code == 200
    data = resp.json()
    assert "stories" in data
    assert len(data["stories"]) >= 2


def test_get_story_detail_success(client, setup_data):
    story1 = setup_data["story1"]
    resp = client.get(f"/stories/{story1.story_id}/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["story_id"] == story1.story_id


def test_get_story_detail_not_found(client):
    resp = client.get("/stories/9999/")
    assert resp.status_code == 404


def test_create_user_success(client):
    payload = {"username": "newuser", "password": "pw1234"}
    resp = client.post(
        "/user/create", data=json.dumps(payload), content_type="application/json"
    )
    assert resp.status_code == 201


def test_create_user_forbidden(client, setup_data):
    alice = setup_data["alice"]
    payload = {"username": alice.username, "password": "pass123"}
    resp = client.post(
        "/user/create", data=json.dumps(payload), content_type="application/json"
    )
    assert resp.status_code == 400


def test_create_story_success(client, setup_data):
    alice = setup_data["alice"]
    proj1 = setup_data["proj1"]
    org1 = setup_data["org1"]

    payload = {
        "story_id": 3,
        "storyteller": "Test T.",
        "curator": alice.user_id,
        "date": "2025-05-10",
        "content": "New test story",
        "proj_id": proj1.proj_id,
        "org_id": org1.org_id,
    }
    resp = client.post(
        "/stories/create/", data=json.dumps(payload), content_type="application/json"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["story_id"] == 3
    assert Story.objects.filter(story_id=3).exists()


def test_create_story_bad_request(client):
    resp = client.post("/stories/create/", data="not json", content_type="application/json")
    assert resp.status_code == 400


def test_create_project_success(client, setup_data):
    org1 = setup_data["org1"]
    brenda = setup_data["brenda"]

    payload = {"org_id": org1.org_id, "name": "New Project", "curator": brenda.user_id, "tags": ["X", "Y"]}
    resp = client.post(
        "/project/create", data=json.dumps(payload), content_type="application/json"
    )
    assert resp.status_code == 201
    data = resp.json()
    assert Project.objects.filter(proj_id=data["project_id"]).exists()


def test_create_project_no_org(client):
    payload = {"name": "NoOrg"}
    resp = client.post(
        "/project/create", data=json.dumps(payload), content_type="application/json"
    )
    assert resp.status_code == 400


def test_create_org_success(client, setup_data):
    alice = setup_data["alice"]
    payload = {"org_id": 99, "name": "XOrg", "user_id": alice.user_id}
    resp = client.post(
        "/org/create/", data=json.dumps(payload), content_type="application/json"
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["org_id"] == 99
    assert Organization.objects.filter(org_id=99).exists()


def test_create_org_bad_request(client):
    resp = client.post("/org/create/", data=json.dumps({}), content_type="application/json")
    assert resp.status_code == 400
