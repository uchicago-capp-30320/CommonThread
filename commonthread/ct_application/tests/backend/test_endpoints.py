# commonthread/ct_application/tests/backend/test_endpoints.py
#
# Run:  pytest -q

import json, datetime, jwt, pytest
from django.utils import timezone
from django.test import Client
from ct_application.models import (
    CustomUser, Organization, OrgUser, Project, Story,
    Tag, StoryTag, ProjectTag
)
from commonthread.settings import JWT_SECRET_KEY


pytestmark = pytest.mark.django_db
# ───────────────────────  DATA SETUP  ────────────────────────────────
@pytest.fixture
def seed():
    """Create two users, two orgs, one project, one story, one tag."""
    alice  = CustomUser.objects.create_user("alice",  "pass123", name="Alice A.")
    brenda = CustomUser.objects.create_user("brenda", "secret456", name="Brenda B.")

    org1 = Organization.objects.create(name="University of Chicago")   # id 1
    org2 = Organization.objects.create(name="Hyde Park Hist. Soc.")    # id 2
    OrgUser.objects.bulk_create([
        OrgUser(user_id=alice,  org_id=org1, access="admin"),
        OrgUser(user_id=brenda, org_id=org2, access="admin"),
    ])

    proj1 = Project.objects.create(org_id=org1, name="Campus Tales",
                                   curator=alice, date="2025‑04‑01")
    story1 = Story.objects.create(proj_id=proj1, storyteller="Alice",
                                  curator=alice, content="Hello world")
    tag1 = Tag.objects.create(name="fun")
    StoryTag.objects.create(story_id=story1, tag_id=tag1)
    ProjectTag.objects.create(proj_id=proj1, tag_id=tag1)

    return locals()          # handy dict access

@pytest.fixture
def client():
    return Client()

# ──────────────────────  AUTH HELPERS  ───────────────────────────────
@pytest.fixture
def auth_headers(seed, client):
    """
    Call like:   hdrs = auth_headers()             # Alice
                 hdrs = auth_headers(user='brenda')# Brenda
    """
    def _login(user="alice", pwd="pass123"):
        body = {"post_data": {"username": user, "password": pwd}}
        res  = client.post("/login", json.dumps(body),
                           content_type="application/json")
        assert res.status_code == 200
        token = res.json()["access_token"]
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}
    return _login

def expired_access_token(user_id: int):
    past = timezone.now() - datetime.timedelta(hours=1, seconds=5)
    payload = {"sub": str(user_id), "iat": past, "exp": past}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

# ───────────────────  PUBLIC / UNGUARDED  ────────────────────────────
def test_home_page(client):
    r = client.get("/")
    assert r.status_code == 200 and b"Welcome" in r.content

def test_login_success(client):
    body = {"post_data": {"username": "alice", "password": "pass123"}}
    r = client.post("/login", json.dumps(body), content_type="application/json")
    assert r.status_code == 200 and "access_token" in r.json()

def test_login_bad_password(client):
    body = {"post_data": {"username": "alice", "password": "oops"}}
    assert client.post("/login", json.dumps(body),
                       content_type="application/json").status_code == 403

# ─────────────────────  REFRESH FLOW  ────────────────────────────────
def test_access_and_refresh_end_to_end(client):
    body = {"post_data": {"username": "alice", "password": "pass123"}}
    login = client.post("/login", json.dumps(body), content_type="application/json")
    refresh = login.json()["refresh_token"]

    r = client.post("/login/create_access",
                    json.dumps({"refresh_token": refresh}),
                    content_type="application/json")
    assert r.status_code == 200
    new_token = r.json()["access_token"]
    # new token actually decodes
    jwt.decode(new_token, JWT_SECRET_KEY, algorithms=["HS256"])

# ───────────────────  PROTECTED – HAPPY PATH  ────────────────────────
def test_org_dashboard_ok(client, seed, auth_headers):
    org = seed["org1"]
    r = client.get(f"/org/1/{org.org_id}/", **auth_headers())
    assert r.status_code == 200 and "stories" in r.json()

def test_project_dashboard_ok(client, seed, auth_headers):
    p = seed["proj1"]
    r = client.get(f"/org/1/{p.org_id.org_id}/project/{p.proj_id}/",
                   **auth_headers())
    assert r.status_code == 200 and r.json()["project_id"] == p.proj_id

def test_story_list_ok(client, auth_headers):
    r = client.get("/stories/", **auth_headers())
    assert r.status_code == 200 and len(r.json()["stories"]) >= 1

def test_story_detail_ok(client, seed, auth_headers):
    s = seed["story1"]
    r = client.get(f"/stories/{s.story_id}/", **auth_headers())
    assert r.status_code == 200 and r.json()["story_id"] == s.story_id

# ───────────────────  CREATE HAPPY PATH  ─────────────────────────────
def test_create_project_ok(client, seed, auth_headers):
    org = seed["org1"]
    payload = {"org_id": org.org_id, "name": "New Proj",
               "curator": seed["alice"].id}
    r = client.post("/project/create", json.dumps(payload),
                    content_type="application/json", **auth_headers())
    assert r.status_code == 201 and "project_id" in r.json()

def test_create_story_ok(client, seed, auth_headers):
    p = seed["proj1"]
    payload = {
        "storyteller": "Test User",
        "curator": seed["alice"].id,
        "content": "Hi!",
        "proj_id": p.proj_id,
        "tags": [{"name":"tagX","value":1}]
    }
    r = client.post("/stories/create/", json.dumps(payload),
                    content_type="application/json", **auth_headers())
    assert r.status_code == 200 and "story_id" in r.json()

# ───────────────────  AUTH EDGE‑CASES  ───────────────────────────────
def test_missing_token_401(client):
    assert client.get("/stories/").status_code == 401

def test_malformed_token_401(client):
    hdrs = {"HTTP_AUTHORIZATION": "Bearer nope.nope.nope"}
    assert client.get("/stories/", **hdrs).status_code == 401

def test_expired_token_401(client, seed):
    bad = expired_access_token(seed["alice"].id)
    hdrs = {"HTTP_AUTHORIZATION": f"Bearer {bad}"}
    assert client.get("/stories/", **hdrs).status_code == 401

def test_forbidden_project_403(client, seed, auth_headers):
    # Brenda token, Alice project → 403
    p = seed["proj1"]
    hdrs = auth_headers(user="brenda", pwd="secret456")
    r = client.get(f"/org/2/{p.org_id.org_id}/project/{p.proj_id}/", **hdrs)
    assert r.status_code == 403

def test_org_dashboard_wrong_user_in_path(client, seed, auth_headers):
    org = seed["org1"]
    r = client.get(f"/org/999/{org.org_id}/", **auth_headers())
    assert r.status_code in (403, 404)

# ───────────  CREATE / VALIDATION EDGE‑CASES  ────────────────────────
def test_create_project_missing_org_400(client, auth_headers):
    r = client.post("/project/create", json.dumps({"name":"X"}),
                    content_type="application/json", **auth_headers())
    assert r.status_code == 400

def test_create_story_bad_json_400(client, auth_headers):
    r = client.post("/stories/create/", "not‑json",
                    content_type="application/json", **auth_headers())
    assert r.status_code == 400

def test_create_org_missing_fields_400(client, auth_headers):
    r = client.post("/org/create/", json.dumps({}),
                    content_type="application/json", **auth_headers())
    assert r.status_code == 400

# ─────────────────────  REFRESH EDGE‑CASES  ──────────────────────────
def test_refresh_missing_token_400(client):
    r = client.post("/login/create_access", json.dumps({}),
                    content_type="application/json")
    assert r.status_code == 400

def test_refresh_invalid_token_401(client):
    r = client.post("/login/create_access",
                    json.dumps({"refresh_token":"bogus"}),
                    content_type="application/json")
    assert r.status_code == 401

# ────────────────────────  COUNT  CHECK  ─────────────────────────────
def test_have_at_least_30_tests():
    # pytest collects test items before running; plug into that list
    import inspect, sys
    items = [name for name, obj in inspect.getmembers(sys.modules[__name__])
             if name.startswith("test_")]
    assert len(items) >= 30
