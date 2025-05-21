# commonthread/ct_application/tests/backend/test_endpoints.py
import json
import datetime
import jwt
import inspect
import sys
import pytest
from django.utils import timezone
from django.test import Client
from ct_application.models import (
    CustomUser, Organization, OrgUser,
    Project, Story, Tag, StoryTag, ProjectTag
)
from commonthread.settings import JWT_SECRET_KEY

pytestmark = pytest.mark.django_db

# ────────────── seed data ──────────────
@pytest.fixture
def seed():
    alice  = CustomUser.objects.create_user(
        "alice", email="alice@example.com",
        password="pass123", name="Alice"
    )
    brenda = CustomUser.objects.create_user(
        "brenda", email="brenda@example.com",
        password="secret456", name="Brenda"
    )
    deleto = CustomUser.objects.create_user(
        "deleto", email="deleto@example.com",
        password="editdeletetester", name="Delly"
    )

    org1, org2, org3 = (
        Organization.objects.create(name="UChicago"),
        Organization.objects.create(name="HP Hist Soc"),
        Organization.objects.create(name="Edit Delete Tester"),
    )
    OrgUser.objects.bulk_create([
        OrgUser(user_id=alice.id,  org_id=org1.id, access="admin"),
        OrgUser(user_id=brenda.id, org_id=org2.id, access="admin"),
        OrgUser(user_id=deleto.id, org_id=org3.id, access="creator"),
    ])

    proj1 = Project.objects.create(
        org_id=org1.id, name="Campus Tales",
        curator=alice, date=datetime.date(2025, 4, 1)
    )
    proj_edit_delete = Project.objects.create(
        org_id=org3.id, name="To Be Edited",
        curator=deleto, date=datetime.date(2025, 4, 7)
    )

    story1 = Story.objects.create(
        proj_id=proj1.id, storyteller="Alice",
        curator=alice, date=datetime.date(2025, 4, 5),
        text_content="Hello!"
    )
    story2 = Story.objects.create(
        proj_id=proj_edit_delete.id, storyteller="Delly",
        curator=deleto, date=datetime.date(2025, 4, 7),
        text_content="To be edited and deleted"
    )
    tag = Tag.objects.create(name="fun", value="yes", required=False)
    StoryTag.objects.create(story_id=story1.id, tag_id=tag.id)
    ProjectTag.objects.create(proj_id=proj1.id, tag_id=tag.id)

    StoryTag.objects.create(story_id=story2.id, tag_id=tag.id)
    ProjectTag.objects.create(proj_id=proj_edit_delete.id, tag_id=tag.id)

    return locals()

@pytest.fixture
def client():
    return Client()

# ─────────── auth helpers ────────────
@pytest.fixture
def auth_headers(seed, client):
    def _login(user="alice", pwd="pass123"):
        body = {"post_data": {"username": user, "password": pwd}}
        res  = client.post("/login", json.dumps(body),
                           content_type="application/json")
        assert res.status_code == 200, res.content
        tok = res.json()["access_token"]
        return {"HTTP_AUTHORIZATION": f"Bearer {tok}"}
    return _login

@pytest.fixture
def auth_headers_user3(seed, client):
    def _login(user="deleto", pwd="editdeletetester"):
        body = {"post_data": {"username": user, "password": pwd}}
        res  = client.post("/login", json.dumps(body),
                           content_type="application/json")
        assert res.status_code == 200, res.content
        tok = res.json()["access_token"]
        return {"HTTP_AUTHORIZATION": f"Bearer {tok}"}
    return _login

def expired_access_token(uid):
    past = timezone.now() - datetime.timedelta(hours=2)
    payload = {"sub": str(uid), "iat": past, "exp": past}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

# ───────── public / auth endpoints ─────────
def test_home_ok(client):
    assert client.get("/").status_code == 200

def test_login_ok(client, seed):
    body = {"post_data": {"username": "alice", "password": "pass123"}}
    r = client.post("/login", json.dumps(body), content_type="application/json")
    assert r.status_code == 200 and "access_token" in r.json()

def test_login_bad_pwd(client, seed):
    body = {"post_data": {"username": "alice", "password": "bad"}}
    assert client.post("/login", json.dumps(body),
                       content_type="application/json").status_code == 403

def test_refresh_ok(client, seed):
    body = {"post_data": {"username": "alice", "password": "pass123"}}
    res  = client.post("/login", json.dumps(body), content_type="application/json")
    ref  = res.json()["refresh_token"]
    r = client.post("/create_access",
                    json.dumps({"refresh_token": ref}),
                    content_type="application/json")
    assert r.status_code == 200 and "access_token" in r.json()

# ───────── protected happy‑paths ─────────
def test_org_dashboard_ok(client, seed, auth_headers):
    _, org1 = seed["alice"], seed["org1"]
    r = client.get(f"/org/{org1.id}", **auth_headers())
    assert r.status_code == 200 and "org_id" in r.json()

def test_project_dashboard_ok(client, seed, auth_headers):
    _, p = seed["alice"], seed["proj1"]
    r = client.get(f"/project/{p.id}", #org1 hardcoded, just to test page working at all
                   **auth_headers())
    assert r.status_code == 200 and r.json()["project_id"] == p.id

def test_story_detail_ok(client, seed, auth_headers):
    s = seed["story1"]
    r = client.get(f"/story/{s.id}", **auth_headers())
    assert r.status_code == 200 and r.json()["story_id"] == s.id

# ───────── create happy‑paths ─────────
def test_create_project_ok(client, seed, auth_headers):
    org1, alice = seed["org1"], seed["alice"]
    payload = {
        "org_id":  org1.id,
        "name":    "New Project",
        "curator": alice.id,
        "date":    "2025-05-01"
    }
    r = client.post("/project/create", json.dumps(payload),
                    content_type="application/json", **auth_headers())
    assert r.status_code == 201

def test_create_story_ok(client, seed, auth_headers):
    p, alice = seed["proj1"], seed["alice"]
    payload = {
        "storyteller": "Testy", "curator": alice.id,
        "text_content": "Hi!", "proj_id": p.id,
        "tags": [{"name": "tagX", "value": 1, "required": False}],
    }
    r = client.post("/story/create", json.dumps(payload),
                    content_type="application/json", **auth_headers())
    assert r.status_code == 200

# ------------------ Edit Tests -----------------------------------

def test_edit_story(client, seed, auth_headers_user3):
    #Curator testing is currently broken.
    p, s, deleto = seed["proj_edit_delete"], seed['story2'], seed["deleto"]
    payload = {"storyteller": "Testy", "curator": deleto.id,
        "text_content": "Content has been Edited", "proj": p.id
    }
    r = client.post(f"/story/{s.id}/edit", json.dumps(payload),
                    content_type="application/json", **auth_headers_user3())
    assert r.status_code == 200

def test_edit_project(client, seed, auth_headers_user3):
    #Curator testing is currently broken.
    p, org3, deleto = seed["proj_edit_delete"], seed['org3'], seed["deleto"]
    payload = {
        "org_id":  org3.id,
        "name":    "Edited Project Name",
        "curator": deleto.id,
        "date":    "2025-05-08"
    }
    r = client.post(f"/project/{org3.id}/{p.id}/edit", json.dumps(payload),
                    content_type="application/json", **auth_headers_user3())
    assert r.status_code == 200

def test_edit_org(client, seed, auth_headers_user3):
    org3, deleto = seed['org3'], seed["deleto"]
    payload = {
        "description":  "Edited Org Description",
        "name":    "Edited Organization Name",
    }
    r = client.post(f"/org/{org3.id}/edit", json.dumps(payload),
                    content_type="application/json", **auth_headers_user3())
    assert r.status_code == 200

def test_edit_user(client, seed, auth_headers):
    pass

# ------------------ Delete Tests ---------------------------------

def test_delete_story(client, seed, auth_headers_user3):
    s, deleto = seed['story2'], seed["deleto"]
    r = client.delete(f"/story/{s.id}/delete", **auth_headers_user3())
    assert r.status_code == 200


def test_delete_project(client, seed, auth_headers_user3):
    o, p, deleto = seed['org3'], seed['proj_edit_delete'], seed["deleto"]
    r = client.delete(f"/project/{o.id}/{p.id}/delete", **auth_headers_user3())
    assert r.status_code == 200

def test_delete_org(client, seed, auth_headers_user3):
    o, deleto = seed['org3'], seed["deleto"]
    r = client.delete(f"/org/{o.id}/delete", **auth_headers_user3())
    assert r.status_code == 200

def test_delete_user(client, seed, auth_headers_user3):
    deleto = seed["deleto"]
    r = client.delete(f"/user/{deleto.id}/delete", **auth_headers_user3())
    assert r.status_code == 200


# ───────── auth / permission edges ─────────
def test_no_token_401(client):
    assert client.get("/story/1").status_code == 401

def test_malformed_token_401(client):
    hdrs = {"HTTP_AUTHORIZATION": "Bearer bad.token"}
    assert client.get("/story/1", **hdrs).status_code == 401

def test_expired_token_299(client, seed):
    hdrs = {"HTTP_AUTHORIZATION":
            f"Bearer {expired_access_token(seed['alice'].id)}"}
    assert client.get("/story/1", **hdrs).status_code == 299

def test_project_forbidden_403(client, seed, auth_headers):
    p = seed["proj1"]
    hdrs = auth_headers("brenda", "secret456")
    r = client.get(f"/project/{p.org_id}/{p.id}",
                   **hdrs)
    assert r.status_code == 403

# ───────── validation edges ─────────
def test_create_project_missing_org_400(client, auth_headers):
    r = client.post("/project/create", json.dumps({"name": "X"}),
                    content_type="application/json", **auth_headers())
    assert r.status_code == 400

def test_create_story_bad_json_400(client, auth_headers):
    r = client.post("/story/create", "not‑json",
                    content_type="application/json", **auth_headers())
    assert r.status_code == 400

def test_create_org_missing_fields_400(client, auth_headers):
    r = client.post("/org/create", json.dumps({}),
                    content_type="application/json", **auth_headers())
    assert r.status_code == 400

# ───────── refresh edges ─────────
def test_refresh_missing_token_400(client):
    r = client.post("/create_access", json.dumps({}),
                    content_type="application/json")
    assert r.status_code == 400

def test_refresh_invalid_token_401(client):
    r = client.post("/create_access",
                    json.dumps({"refresh_token": "bogus"}),
                    content_type="application/json")
    assert r.status_code == 401

# ───────── count guard ─────────
def test_have_at_least_18_tests():
    assert sum(n.startswith("test_")
               for n, _ in inspect.getmembers(sys.modules[__name__])) >= 18
