# ct_application/tests.py

import json
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from ct_application import views
from ct_application.models import (
    Organization,
    OrgUser,
    Project,
    Story,
    Tag,
    StoryTag,
    ProjectTag,
    UserLogin,
)

User = get_user_model()


class ViewTests(TestCase):
    def setUp(self):
        # RequestFactory for direct view calls
        # This allows us to create mock http requests for testing
        # https://medium.com/@altafkhan_24475/part-8-an-overview-of-request-factory-in-django-testing-d60de51b8e19
        # https://docs.djangoproject.com/en/4.2/topics/testing/tools/#requestfactory
        self.factory = RequestFactory()

        # Mock Users for testing
        self.alice = User.objects.create_user(
            username="alice",
            password="pass123",
            name="Alice Anderson",
            email="alice@uchicago.edu",
        )

        self.brenda = User.objects.create_user(
            username="brenda",
            password="secret456",
            name="Brenda Brown",
            email="brenda@uchicago.edu",
        )

        # Link into UserLogin
        UserLogin.objects.create(
            user_id=self.alice, username="alice", password="pass123"
        )
        UserLogin.objects.create(
            user_id=self.brenda, username="brenda", password="secret456"
        )

        # Orgs
        self.org1 = Organization.objects.create(name="University of Chicago")
        self.org2 = Organization.objects.create(name="Hyde Park Historical Society")
        self.org3 = Organization.objects.create(name="Chicago Story Guild")

        # OrgUser
        OrgUser.objects.create(user_id=self.alice, org_id=self.org1, access="admin")
        OrgUser.objects.create(user_id=self.brenda, org_id=self.org2, access="admin")
        OrgUser.objects.create(user_id=self.alice, org_id=self.org3, access="admin")

        # Projects
        self.proj1 = Project.objects.create(
            org_id=self.org1, name="Campus Tales", curator=self.alice, date="2025-04-01"
        )
        self.proj2 = Project.objects.create(
            org_id=self.org2, name="Memory Lane", curator=self.brenda, date="2025-03-15"
        )
        self.proj3 = Project.objects.create(
            org_id=self.org3,
            name="Windy City Whispers",
            curator=self.alice,
            date="2025-02-20",
        )

        # Stories
        self.story1 = Story.objects.create(
            proj_id=self.proj1,
            org_id=self.org1,
            storyteller="Alice A.",
            curator=self.alice,
            date="2025-04-05",
            content="Story one content",
        )
        self.story2 = Story.objects.create(
            proj_id=self.proj1,
            org_id=self.org1,
            storyteller="Bob B.",
            curator=self.brenda,
            date="2025-04-10",
            content="Story two content",
        )

        # --- Tags & link tables ---
        self.tag1 = Tag.objects.create(name="Fun")
        self.tag2 = Tag.objects.create(name="Sad")
        StoryTag.objects.create(story_id=self.story1, tag_id=self.tag1)
        ProjectTag.objects.create(proj_id=self.proj1, tag_id=self.tag1)

    def test_home_test(self):
        request = self.factory.get("/")
        response = views.home_test(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Welcome to the Common Threads Home Page!")

    def test_login_success(self):
        payload = {"username": self.alice.username, "password": self.alice.password}
        body    = json.dumps(payload)
        request = self.factory.post(
            "/login",
            data=body,
            content_type="application/json"
        )
        response = views.login(request)
        self.assertEqual(response.status_code, 200)

    def test_login_forbiden(self):
        payload = {
            "username": self.alice.username,
            "password": self.alice.password + "additional_chars",
        }
        body    = json.dumps(payload)
        request = self.factory.post(
            "/login",
            data=body,
            content_type="application/json"
        )
        response = views.login(request)
        self.assertEqual(response.status_code, 403)
    
    def test_refresh_success(self):
        body = json.dumps({"username": self.alice.username, "password": "pass123"})
        req  = self.factory.post("/login", data=body, content_type="application/json")
        login_resp = views.login(req)
        refresh_t  = json.loads(login_resp.content)["refresh_token"]

        body = json.dumps({"refresh_token": refresh_t})
        req  = self.factory.post("/login/create_access", data=body, content_type="application/json")
        resp = views.get_new_access_token(req)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertTrue(data["success"])
        self.assertIn("access_token", data)


    def test_show_project_dashboard_success(self):
        req = self.factory.get("/")
        resp = views.show_project_dashboard(
            req, self.alice.user_id, self.org1.org_id, self.proj1.proj_id
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data["project_id"], self.proj1.proj_id)
        self.assertEqual(data["story_count"], 2)
        self.assertEqual(data["tag_count"], 1)

    def test_show_project_dashboard_forbidden(self):
        req = self.factory.get("/")
        resp = views.show_project_dashboard(
            req, self.brenda.user_id, self.org1.org_id, self.proj1.proj_id
        )
        self.assertEqual(resp.status_code, 403)

    def test_show_org_dashboard_success(self):
        req = self.factory.get("/")
        resp = views.show_org_dashboard(req, self.alice.user_id, self.org1.org_id)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data["organization_id"], self.org1.org_id)
        self.assertEqual(data["project_count"], 1)

    def test_show_org_dashboard_forbidden(self):
        req = self.factory.get("/")
        resp = views.show_org_dashboard(req, self.alice.user_id, self.org2.org_id)
        self.assertEqual(resp.status_code, 403)

    def test_get_story_list(self):
        req = self.factory.get("/")
        resp = views.get_story(req)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIn("stories", data)
        self.assertGreaterEqual(len(data["stories"]), 2)

    def test_get_story_detail_success(self):
        req = self.factory.get("/")
        resp = views.get_story(req, story_id=self.story1.story_id)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data["story_id"], self.story1.story_id)

    def test_get_story_detail_not_found(self):
        req = self.factory.get("/")
        resp = views.get_story(req, story_id=9999)
        self.assertEqual(resp.status_code, 404)

    def test_create_user_success(self):
        payload = {"username": "Alessandro", "password": "Reynosa124"}
        req = self.factory.post(
            "/user/create", data=json.dumps(payload), content_type="application/json"
        )

        resp = views.create_user(req)
        self.assertEqual(resp.status_code, 201)

    def test_create_user_forbidden(self):
        """
        Test adding a user that already exists
        """
        payload = {"username": self.alice.username, "password": self.alice.password}
        req = self.factory.post(
            "/user/create", data=json.dumps(payload), content_type="application/json"
        )

        resp = views.create_user(req)
        self.assertEqual(resp.status_code, 400)

    def add_user_to_org_sucess(self):
        payload = {"user_id": self.alice.user_id, "org_id": self.org1.org_id}
        req = self.factory.post(
            "/user/create", data=json.dumps(payload), content_type="application/json"
        )

        resp = views.create_user(req)
        self.assertEqual(resp.status_code, 201)

    def test_create_story_success(self):
        payload = {
            "story_id": 3,
            "storyteller": "Test T.",
            "curator": self.alice.user_id,
            "date": "2025-05-10",
            "content": "New test story",
            "proj_id": self.proj1.proj_id,
            "org_id": self.org1.org_id,
        }
        req = self.factory.post(
            "/", data=json.dumps(payload), content_type="application/json"
        )
        resp = views.create_story(req)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data["story_id"], 3)
        self.assertTrue(Story.objects.filter(story_id=3).exists())

    def test_create_story_bad_request(self):
        req = self.factory.post("/", data="not json", content_type="application/json")
        resp = views.create_story(req)
        self.assertEqual(resp.status_code, 400)

    def test_create_project_success(self):
        payload = {
            "org_id": self.org1.org_id,
            "name": "New Project",
            "curator": self.brenda.user_id,
            "tags": ["X", "Y"],
        }
        req = self.factory.post(
            "/", data=json.dumps(payload), content_type="application/json"
        )
        resp = views.create_project(req)
        self.assertEqual(resp.status_code, 201)
        data = json.loads(resp.content)
        self.assertTrue(Project.objects.filter(proj_id=data["project_id"]).exists())

    def test_create_project_no_org(self):
        payload = {"name": "NoOrg"}
        req = self.factory.post(
            "/", data=json.dumps(payload), content_type="application/json"
        )
        resp = views.create_project(req)
        self.assertEqual(resp.status_code, 400)

    def test_create_org_success(self):
        payload = {"org_id": 99, "name": "XOrg", "user_id": self.alice.user_id}
        req = self.factory.post(
            "/", data=json.dumps(payload), content_type="application/json"
        )
        resp = views.create_org(req)
        self.assertEqual(resp.status_code, 201)
        data = json.loads(resp.content)
        self.assertEqual(data["org_id"], 99)
        self.assertTrue(Organization.objects.filter(org_id=99).exists())

    def test_create_org_bad_request(self):
        req = self.factory.post(
            "/", data=json.dumps({}), content_type="application/json"
        )
        resp = views.create_org(req)
        self.assertEqual(resp.status_code, 400)
