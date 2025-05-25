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
    MLProcessingQueue,
    CustomUser, Organization, OrgUser,
    Project, Story, Tag, StoryTag, ProjectTag
)
from commonthread.settings import JWT_SECRET_KEY
from unittest.mock import patch, MagicMock
from django.conf import settings
from django.urls import reverse
from ct_application import views

pytestmark = pytest.mark.django_db

# ────────────── seed data ──────────────
@pytest.fixture
def seed():
    # ─── Users ───
    alice = CustomUser.objects.create_user(
        username="alice",
        email="alice@example.com",
        password="pass123",
        name="Alice"
    )
    brenda = CustomUser.objects.create_user(
        username="brenda",
        email="brenda@example.com",
        password="secret456",
        name="Brenda"
    )
    deleto = CustomUser.objects.create_user(
        username="deleto",
        email="deleto@example.com",
        password="editdeletetester",
        name="Delly"
    )

    # ─── Organizations ───
    org1 = Organization.objects.create(name="UChicago")
    org2 = Organization.objects.create(name="HP Hist Soc")
    org3 = Organization.objects.create(name="Edit Delete Tester")

    # ─── Memberships ───
    OrgUser.objects.bulk_create([
        OrgUser(user=alice,  org=org1, access="admin"),
        OrgUser(user=brenda, org=org2, access="admin"),
        OrgUser(user=deleto, org=org3, access="creator"),
        OrgUser(user=alice, org=org3, access="user"),
    ])

    # ─── Projects ───
    proj1 = Project.objects.create(
        org=org1,
        name="Campus Tales",
        curator=alice,
        date=datetime.date(2025, 4, 1)
    )
    proj_edit_delete = Project.objects.create(
        org=org3,
        name="To Be Edited",
        curator=deleto,
        date=datetime.date(2025, 4, 7)
    )

    # ─── Stories ───
    story1 = Story.objects.create(
        proj=proj1,
        storyteller="Alice",
        curator=alice,
        date=datetime.date(2025, 4, 5),
        text_content="Hello!",
        summary="summarized",
        is_transcript=False
    )
    story2 = Story.objects.create(
        proj=proj_edit_delete,
        storyteller="Delly",
        curator=deleto,
        date=datetime.date(2025, 4, 7),
        text_content="To be edited and deleted",
        summary="summarized",
        is_transcript=False
    )

    # ─── Tagging ───
    tag = Tag.objects.create(name="fun", value="yes", required=False)
    StoryTag.objects.create(story=story1, tag=tag)
    ProjectTag.objects.create(proj=proj1, tag=tag)
    StoryTag.objects.create(story=story2, tag=tag)
    ProjectTag.objects.create(proj=proj_edit_delete, tag=tag)

    return {
        "alice": alice,
        "brenda": brenda,
        "deleto": deleto,
        "org1": org1,
        "org2": org2,
        "org3": org3,
        "proj1": proj1,
        "proj_edit_delete": proj_edit_delete,
        "story1": story1,
        "story2": story2,
        "tag": tag,
    }

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
    body = {"post_data": {"username": "alice", "password": "badbadbad"}}
    assert client.post("/login", json.dumps(body),
                       content_type="application/json").status_code == 403

def test_login_no_password(client, seed):
    body = {"post_data": {"username": "alice"}}
    assert client.post("/login", json.dumps(body),
                       content_type="application/json").status_code == 400
    
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

@pytest.mark.django_db
def test_get_ml_status_ok_independent(client):
    # 1) build your own Org → User → Project → Story → MLTask chain
    org     = Organization.objects.create(name="Test Org")
    user    = CustomUser.objects.create_user(
        username="alice", password="pw123", email="a@e.com"
    )
    project = Project.objects.create(
        org=org,
        curator=user,
        name="ML Test Project",
        date=datetime.date(2025, 5, 23)
    )
    story   = Story.objects.create(
        proj=project,
        storyteller="bob",
        curator=user,
        date=datetime.date(2025, 5, 23),
        text_content="hello world",
        is_transcript=False
    )
    ml_task = MLProcessingQueue.objects.create(
        story=story,
        project=project,
        task_type="tag",
        status="processing"
    )

    # 2) call the endpoint
    resp = client.get(f"/story/{story.id}/ml-status")
    assert resp.status_code == 200

    data = resp.json()
    assert data["success"]    is True
    assert data["task_type"]  == "tag"
    assert data["ml_status"]  == "processing"

    # timestamp should be an ISO timestamp within a few seconds of now
    ts = datetime.datetime.fromisoformat(data["timestamp"])
    assert abs((ts - timezone.now()).total_seconds()) < 10

@pytest.mark.django_db
def test_get_ml_status_not_found_independent(client):
    # no MLProcessingQueue exists for story=9999
    resp = client.get("/story/9999/ml-status")
    assert resp.status_code == 404
    assert resp.json() == {"success": False, "error": "ML status not found"}

# ───────── create happy‑paths ─────────
def test_create_project_ok(client, seed, auth_headers):
    org1, alice = seed["org1"], seed["alice"]
    payload = {
        "org_id":  org1.id,
        "name":    "New Project",
        "description": "New Project Description",
        "curator": alice.id,
    }
    r = client.post("/project/create", json.dumps(payload),
                    content_type="application/json", **auth_headers())
    assert r.status_code == 201

def test_create_story_get_url(client, seed, auth_headers):
    r = client.get("/story/create", **auth_headers())
    assert r.status_code == 200

@pytest.fixture
def mock_s3_presigned():
    return {
        "url": "https://fake-s3-url.com",
        "fields": {"key": "value"}
    }

@pytest.fixture
def basic_story_payload(seed):
    p, alice = seed["proj1"], seed["alice"]
    return {
        "storyteller": "Test Storyteller",
        "curator": alice.id,
        "text_content": "Test story content",
        "project_id": p.id,
        "required_tags": [{"name": "tag1", "value": "value1", "created_by": "human"}],
        "optional_tags": [{"name": "tag2", "value": "value2", "created_by": "human"}]
    }

@patch('ct_application.views.generate_s3_presigned')
def test_create_story_get_presigned_urls(mock_generate_presigned, client, auth_headers):
    mock_generate_presigned.return_value = {
        "url": "https://fake-s3-url.com",
        "fields": {"key": "value"}
    }
    
    response = client.get("/story/create", **auth_headers())
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "audio_upload" in data
    assert "image_upload" in data
    assert data["audio_upload"]["url"] == "https://fake-s3-url.com"
    assert data["image_upload"]["url"] == "https://fake-s3-url.com"

def test_create_story_get_unauthorized(client):
    response = client.get("/story/create")
    assert response.status_code == 401

def test_create_story_basic(client, auth_headers, basic_story_payload):
    response = client.post(
        "/story/create",
        data=json.dumps(basic_story_payload),
        content_type="application/json",
        **auth_headers()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "story_id" in data
    
    story = Story.objects.get(id=data["story_id"])
    assert story.storyteller == basic_story_payload["storyteller"]
    assert story.text_content == basic_story_payload["text_content"]
    
    story_tags = StoryTag.objects.filter(story_id=story.id)
    assert story_tags.count() == 2

def test_create_story_with_media(client, auth_headers, basic_story_payload):
    payload = basic_story_payload.copy()
    payload.update({
        "audio_path": "user/123/audio.mp3",
        "image_path": "user/123/image.jpg"
    })
    
    response = client.post(
        "/story/create",
        data=json.dumps(payload),
        content_type="application/json",
        **auth_headers()
    )
    
    assert response.status_code == 200
    story = Story.objects.get(id=response.json()["story_id"])
    assert story.audio_content == "user/123/audio.mp3"
    assert story.image_content == "user/123/image.jpg"

def test_create_story_invalid_project(client, auth_headers, basic_story_payload):
    payload = basic_story_payload.copy()
    payload["project_id"] = 99999  
    
    response = client.post(
        "/story/create",
        data=json.dumps(payload),
        content_type="application/json",
        **auth_headers()
    )
    # Fails on the project not found
    assert response.status_code == 404
    #assert "Project with ID" in response.json()["error"]

def test_create_story_missing_required_fields(client, auth_headers):
    payload = {"storyteller": "Test"}  
    
    response = client.post(
        "/story/create",
        data=json.dumps(payload),
        content_type="application/json",
        **auth_headers()
    )
    
    assert response.status_code == 400

def test_create_story_invalid_json(client, auth_headers):
    response = client.post(
        "/story/create",
        data="invalid json",
        content_type="application/json",
        **auth_headers()
    )
    
    assert response.status_code == 400

@patch('ct_application.views.QueueProducer')
def test_create_story_queue_failure(mock_queue_producer, client, auth_headers, basic_story_payload):
    mock_producer = MagicMock()
    mock_producer.add_to_queue.return_value = {"success": False}
    mock_queue_producer.return_value = mock_producer
    
    response = client.post(
        "/story/create",
        data=json.dumps(basic_story_payload),
        content_type="application/json",
        **auth_headers()
    )
    
    assert response.status_code == 200
    assert "story_id" in response.json()

def test_add_user_to_org(client, seed, auth_headers):
    alice = seed['alice']
    brenda = seed["brenda"]
    org1 = seed["org1"]
    payload = {
        "user_id": brenda.id,
        "access": "user"
    }
    r = client.post(
        f"/org/{org1.id}/add-user/{brenda.id}",
        data=json.dumps(payload),
        content_type="application/json",
        **auth_headers()
    )
    assert r.status_code == 201
    assert OrgUser.objects.filter(user_id=brenda.id, org_id=org1.id).exists()

def test_create_user_ok(client):
    payload = {
        "username":   "newtester",
        "password":   "securePass123",
        "first_name": "New",
        "last_name":  "Tester",
        "email":      "new@test.com",
        "city":       "Testville"
    }
    resp = client.post(
        "/user/create",
        json.dumps(payload),
        content_type="application/json"
    )
    assert resp.status_code == 201
    data = resp.json()
    # Should return success + an auto-generated user_id
    assert data["success"] is True
    assert isinstance(data.get("user_id"), int)

    # And the user really exists in the DB
    assert CustomUser.objects.filter(username="newtester").exists()

@pytest.mark.django_db
def test_create_org_ok(client, seed, auth_headers):
    alice = seed["alice"]
    payload = {
        "name": "New Org",
        "description": "This is a new org",
        # note: the view ignores a "creator" field and uses request.user_id 
        # so you don't need to include it here
    }
    resp = client.post(
        "/org/create",
        json.dumps(payload),
        content_type="application/json",
        **auth_headers()
    )
    assert resp.status_code == 201

    data = resp.json()
    assert data["success"] is True
    assert isinstance(data.get("org_id"), int)

    # make sure it actually hit the DB
    assert Organization.objects.filter(id=data["org_id"], name="New Org").exists()

@pytest.mark.django_db
def test_get_stories_by_story_id(client, seed):
    """
    If you call /stories/?story_id=<id>, you get back exactly that story
    and the correct id_type/id_value metadata.
    """
    story1 = seed["story1"]
    tag     = seed["tag"]

    resp = client.get(f"/stories/?story_id={story1.id}")
    assert resp.status_code == 200

    data = resp.json()
    # metadata
    assert data["id_type"]  == ["story_id"]
    assert data["id_value"] == [str(story1.id)]

    # exactly one story returned, matching seed["story1"]
    assert len(data["stories"]) == 1
    s = data["stories"][0]
    assert s["story_id"]     == story1.id
    assert s["storyteller"]  == story1.storyteller
    assert s["project_id"]   == story1.proj.id
    assert s["project_name"] == story1.proj.name
    assert s["curator"]      == story1.curator.name
    assert s["date"]         == str(story1.date)
    assert s["summary"]      == story1.summary
    assert s["text_content"] == story1.text_content

    # tags were serialized properly
    assert isinstance(s["tags"], list)
    assert any(t["name"] == tag.name and t["value"] == tag.value for t in s["tags"])

@pytest.mark.django_db
def test_get_story_ok(client, seed, auth_headers):
    """
    Retrieving an existing story with no audio/image content
    should return status 200 with empty audio_path and image_path.
    """
    story = seed["story1"]

    resp = client.get(f"/story/{story.id}", **auth_headers())
    assert resp.status_code == 200

    data = resp.json()
    assert data["story_id"]     == story.id
    assert data["project_id"]   == story.proj.id
    assert data["project_name"] == story.proj.name
    assert data["storyteller"]  == story.storyteller
    assert data["curator"]      == story.curator.id
    assert data["date"]         == str(story.date)
    assert data["text_content"] == story.text_content
    assert data["summary"] == story.summary

    # tags should be a list of {name,value} dicts
    assert isinstance(data["tags"], list)
    for t in data["tags"]:
        assert "name" in t and "value" in t

    # no media on seed → empty strings
    assert data["audio_path"] == ""
    assert data["image_path"] == ""

@pytest.mark.django_db
def test_get_story_with_media(client, seed, monkeypatch, auth_headers):
    """
    If story.audio_content and story.image_content are set, 
    the view should call generate_s3_presigned with the right
    bucket names and return its URL in both audio_path and image_path.
    """
    # Arrange: pick a seeded story and give it "files"
    story = seed["story1"]
    story.audio_content.name = "foo.mp3"
    story.image_content.name = "bar.png"
    story.save()

    # Patch the actual buckets your view expects to match your env
    monkeypatch.setattr(
        settings,
        "CT_BUCKET_AUDIO",
        settings.CT_BUCKET_STORY_AUDIO,
        raising=False
    )
    monkeypatch.setattr(
        settings,
        "CT_BUCKET_IMAGES",
        settings.CT_BUCKET_STORY_IMAGES,
        raising=False
    )

    # Stub out presigning so we know exactly what URL comes back
    monkeypatch.setattr(
        views,
        "generate_s3_presigned",
        lambda **kwargs: {"url": "http://example.com/media"}
    )

    # Act
    resp = client.get(f"/story/{story.id}", **auth_headers())
    assert resp.status_code == 200

    data = resp.json()
    # Assert both paths use our dummy URL
    assert data["audio_path"] == "http://example.com/media"
    assert data["image_path"] == "http://example.com/media"


#-----------error tests-------------------

def test_create_user_conflict(client, seed):
    # 'alice' was created by seed fixture
    payload = {"username": "alice", "password": "whatever"}
    resp = client.post(
        "/user/create",
        json.dumps(payload),
        content_type="application/json"
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "success": False,
        "error": "Username already exists"
    }

def test_create_user_missing_fields(client):
    # No username or password
    resp = client.post(
        "/user/create",
        json.dumps({}),
        content_type="application/json"
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "success": False,
        "error": "Username and password are required"
    }

def test_create_user_invalid_json(client):
    resp = client.post(
        "/user/create",
        "this-is-not-json",
        content_type="application/json"
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "success": False,
        "error": "Invalid JSON"
    }

@pytest.mark.django_db
def test_get_project_method_not_allowed(client, seed):
    # GET-only endpoint (require_GET) should reject POST with 405
    p = seed["proj1"]
    r = client.post(f"/project/{p.id}")
    assert r.status_code == 405

@pytest.mark.django_db
def test_get_project_not_found(client, auth_headers):
    # no project with id=9999 → should return 404 & correct JSON
    r = client.get("/project/9999", **auth_headers())
    assert r.status_code == 404
    text = r.content.decode()
    assert "Project not found" in text

@pytest.mark.django_db
def test_get_org_not_found(client, auth_headers):
    # get_object_or_404 raises Http404, but view catches Exception → 500
    r = client.get("/org/9999", **auth_headers())
    assert r.status_code == 404
    text = r.content.decode()
    assert "Org not found" in text

@pytest.mark.django_db
def test_get_org_unauthorized(client, seed):
    org1 = seed["org1"]
    resp = client.get(f"/org/{org1.id}")
    assert resp.status_code == 401
    assert resp.json() == {"success": False, "error": "No token"}

@pytest.mark.django_db
def test_create_org_missing_name(client, auth_headers):
    # no name or description → first validation error is missing name
    resp = client.post(
        "/org/create",
        json.dumps({}),
        content_type="application/json",
        **auth_headers()
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "success": False,
        "error": "Organization name is required"
    }

@pytest.mark.django_db
def test_create_org_missing_description(client, auth_headers):
    # name present but description missing
    payload = {"name": "Test Org"}
    resp = client.post(
        "/org/create",
        json.dumps(payload),
        content_type="application/json",
        **auth_headers()
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "success": False,
        "error": "Organization description is required"
    }

@pytest.mark.django_db
def test_get_user_no_token(client):
    # No Authorization header → 401 + "No token"
    resp = client.get("/user/")
    assert resp.status_code == 401
    assert resp.json() == {"success": False, "error": "No token"}

@pytest.mark.django_db
def test_get_user_bad_token(client):
    # Malformed / unverifiable token → 401 + "Bad token"
    resp = client.get(
        "/user/",
        HTTP_AUTHORIZATION="Bearer not.a.valid.jwt"
    )
    assert resp.status_code == 401
    assert resp.json() == {"success": False, "error": "Bad token"}

@pytest.mark.django_db
def test_get_user_ok(client, seed, auth_headers):
    alice = seed["alice"]
    org1  = seed["org1"]

    resp = client.get("/user/", **auth_headers())
    assert resp.status_code == 200

    data = resp.json()
    # Basic scalar fields
    assert data["user_id"]    == alice.id
    assert data["name"]       == alice.name
    assert data["first_name"] == alice.first_name
    assert data["last_name"]  == alice.last_name
    assert data["email"]      == alice.email
    assert data["city"]       == alice.city
    assert data["bio"]        == alice.bio
    assert data["position"]   == alice.position

    # Profile URL should be a presigned S3 URL
    user_prefix = f"https://{settings.CT_BUCKET_USER_PROFILES}.s3.amazonaws.com/"
    assert isinstance(data["profile_pic_path"], str)
    assert data["profile_pic_path"].startswith(user_prefix)

    # There should be exactly one org entry for org1
    org_entries = [o for o in data["orgs"] if o["org_id"] == str(org1.id)]
    assert len(org_entries) == 1
    org_entry = org_entries[0]
    assert org_entry["org_name"] == org1.name

    # And its profile URL should also be a presigned S3 URL
    org_prefix = f"https://{settings.CT_BUCKET_ORG_PROFILES}.s3.amazonaws.com/"
    assert isinstance(org_entry["org_profile_pic_path"], str)
    assert org_entry["org_profile_pic_path"].startswith(org_prefix)

@pytest.mark.django_db
def test_get_stories_no_filter(client):
    """
    If you call /stories/ with no query params, 
    you must get a 400 and the correct error message.
    """
    resp = client.get("/stories/")
    assert resp.status_code == 400
    assert resp.json() == {
        "error": "Specify exactly one of org_id, project_id, story_id, or user_id."
    }

@pytest.mark.django_db
def test_get_stories_multiple_filters(client, seed):
    """
    If you call /stories/ with more than one filter (e.g. org_id + project_id),
    you must get a 400 and the same error message.
    """
    org1    = seed["org1"]
    proj1   = seed["proj1"]
    resp = client.get(f"/stories/?org_id={org1.id}&project_id={proj1.id}")
    assert resp.status_code == 400
    assert resp.json() == {
        "error": "Specify exactly one of org_id, project_id, story_id, or user_id."
    }

@pytest.mark.django_db
def test_get_story_not_found(client, auth_headers):
    """
    Requesting a non-existent story ID should return the custom
    HttpResponseNotFound message with status 404.
    """
    resp = client.get("/story/9999", **auth_headers())
    assert resp.status_code == 404

    text = resp.content.decode()
    assert "Story not found" in text
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
def test_delete_user_from_org(client, seed, auth_headers_user3):
    deleto, alice, org = seed["deleto"], seed["alice"], seed["org3"]
    r = client.delete(f"/org/{org.id}/delete-user/{alice.id}", **auth_headers_user3())
    assert r.status_code == 200

# ───────── auth / permission edges ─────────
def test_no_token_401(client, seed):
    s = seed['story1']
    assert client.get(f"/story/{s.id}").status_code == 401

def test_malformed_token_401(client, seed):
    s = seed['story1']
    hdrs = {"HTTP_AUTHORIZATION": "Bearer bad.token"}
    assert client.get(f"/story/{s.id}", **hdrs).status_code == 401

def test_expired_token_299(client, seed):
    s, alice = seed['story1'], seed['alice']
    hdrs = {"HTTP_AUTHORIZATION":
            f"Bearer {expired_access_token(alice.id)}"}
    assert client.get(f"/story/{s.id}", **hdrs).status_code == 299

def test_project_forbidden_403(client, seed, auth_headers):
    p = seed["proj1"]
    hdrs = auth_headers("brenda", "secret456")
    r = client.get(f"/project/{p.id}",
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

@pytest.fixture
def refresh_token(seed, client):
    """Fixture to get a valid refresh token through login"""
    body = {"post_data": {"username": "alice", "password": "pass123"}}
    res = client.post("/login", json.dumps(body), content_type="application/json")
    assert res.status_code == 200
    return res.json()["refresh_token"]

def test_get_new_access_token_success(client, refresh_token):
    """Test successful token refresh"""
    response = client.post(
        "/create_access",
        data=json.dumps({"refresh_token": refresh_token}),
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data

def test_get_new_access_token_refresh_token_missing(client):
    """Test error when refresh token is missing"""
    response = client.post(
        "/create_access",
        data=json.dumps({}),
        content_type="application/json"
    )
    
    assert response.status_code == 401


def test_get_new_access_token_refresh_token_invalid_json(client):
    """Test error when request body is not valid JSON"""
    response = client.post(
        "/create_access",
        data="not-json-data",
        content_type="application/json"
    )
    
    assert response.status_code == 400


def test_get_new_access_token_refresh_token_expired(client):
    """Test error when refresh token is expired"""
    past = timezone.now() - datetime.timedelta(days=8)
    payload = {"sub": "1", "iat": past, "exp": past}
    expired_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    
    response = client.post(
        "/create_access",
        data=json.dumps({"refresh_token": expired_token}),
        content_type="application/json"
    )
    
    assert response.status_code == 401


def test_get_new_access_token_refresh_token_invalid(client):
    """Test error when refresh token is invalid"""
    response = client.post(
        "/create_access",
        data=json.dumps({"refresh_token": "invalid.token.here"}),
        content_type="application/json"
    )
    
    assert response.status_code == 401


@patch('ct_application.views.decode_refresh_token')
def test_get_new_access_token_unexpected_error(mock_decode, client, refresh_token):
    """Test handling of unexpected errors during token refresh"""
    mock_decode.side_effect = Exception("Unexpected error")
    
    response = client.post(
        "/create_access",
        data=json.dumps({"refresh_token": refresh_token}),
        content_type="application/json"
    )
    
    assert response.status_code == 500


def test_get_new_access_token_wrong_method(client, refresh_token):
    """Test that only POST method is allowed"""
    response = client.get("/create_access")
    assert response.status_code == 405


