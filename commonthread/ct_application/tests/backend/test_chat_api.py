import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, ANY
from django.conf import settings

from commonthread.ct_application.models import Project, Story, Organization

User = get_user_model()

class ProjectChatAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='test@example.com', name='Test User')
        # Note: Client().login() returns True if login is successful, False otherwise.
        # We don't need to assign it to self.client if we are creating a new client instance each time or just using self.client
        login_successful = self.client.login(username='testuser', password='password123')
        self.assertTrue(login_successful, "Client login failed")

        self.organization = Organization.objects.create(name='Test Org')
        self.project = Project.objects.create(name='Test Project', org=self.organization, date='2023-01-01', curator=self.user)
        
        # Create some stories for context
        Story.objects.create(proj=self.project, text_content="First story about cats.", storyteller="User1", curator=self.user, date="2023-01-02")
        Story.objects.create(proj=self.project, text_content="Second story about dogs.", storyteller="User2", curator=self.user, date="2023-01-03")
        
        self.chat_url = reverse('project-chat-api', kwargs={'project_id': self.project.id})
        self.valid_payload = {"user_message": "Hello AI"}

    def test_chat_api_unauthenticated(self):
        self.client.logout()
        response = self.client.post(self.chat_url, self.valid_payload, content_type='application/json')
        # The verify_user decorator returns 299 if token is expired, 401 if no token or bad token
        # For a logged-out client (no session, no token in header for API calls), it should be 401
        self.assertEqual(response.status_code, 401) # Or 299 if verify_user behaves that way without a token

    @patch('commonthread.ct_application.ml.perplexity_service.get_perplexity_chat_response')
    def test_chat_api_success(self, mock_get_perplexity_chat_response):
        mock_get_perplexity_chat_response.return_value = {
            "choices": [{"message": {"content": "Mocked AI response"}}],
            "usage": {"total_tokens": 50} # Example other data
        }

        response = self.client.post(self.chat_url, self.valid_payload, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json.get('reply'), "Mocked AI response")

        expected_context = "First story about cats.\n\nSecond story about dogs."
        mock_get_perplexity_chat_response.assert_called_once_with(
            settings.PERPLEXITY_API_KEY,
            expected_context,
            self.valid_payload['user_message']
        )

    def test_chat_api_missing_message(self):
        response = self.client.post(self.chat_url, {}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertIn("Missing user_message", response_json.get('error', ''))

    def test_chat_api_invalid_json(self):
        response = self.client.post(self.chat_url, "this is not json", content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertIn("Invalid JSON", response_json.get('error', ''))

    @patch('commonthread.ct_application.ml.perplexity_service.get_perplexity_chat_response')
    def test_chat_api_perplexity_service_error(self, mock_get_perplexity_chat_response):
        mock_get_perplexity_chat_response.return_value = {
            "error": "Perplexity API unavailable", 
            "details": "Service is down",
            "status_code": 503
        }

        response = self.client.post(self.chat_url, self.valid_payload, content_type='application/json')
        
        self.assertEqual(response.status_code, 503)
        response_json = response.json()
        self.assertEqual(response_json.get('error'), "Failed to get response from AI service")
        self.assertIn("Perplexity API unavailable", response_json.get('details', ''))

    def test_chat_api_project_not_found(self):
        # Create a URL for a non-existent project ID
        # Assuming UUIDs for IDs, generate a new one or use a large integer if using integer IDs
        non_existent_project_id = self.project.id + 999 # Or a random UUID if using UUIDs
        chat_url_not_found = reverse('project-chat-api', kwargs={'project_id': non_existent_project_id})
        
        # Make the POST request
        response = self.client.post(chat_url_not_found, self.valid_payload, content_type='application/json')
        
        # Check the response status code.
        # The verify_user decorator's id_searcher calls check_project_auth,
        # which returns a JsonResponse with status 404 if Project.DoesNotExist.
        # The auth_level_check then would receive this JsonResponse and return it.
        self.assertEqual(response.status_code, 404)
        response_json = response.json()
        self.assertIn("Project not found", response_json.get('error', ''))

    # Test for when Perplexity response is missing the expected 'content'
    @patch('commonthread.ct_application.ml.perplexity_service.get_perplexity_chat_response')
    def test_chat_api_perplexity_malformed_success_response(self, mock_get_perplexity_chat_response):
        mock_get_perplexity_chat_response.return_value = {
            "choices": [{"message": {"text_instead_of_content": "Mocked AI response"}}], # Malformed
            "usage": {"total_tokens": 50}
        }

        response = self.client.post(self.chat_url, self.valid_payload, content_type='application/json')
        
        self.assertEqual(response.status_code, 500) # Internal server error due to unexpected structure
        response_json = response.json()
        self.assertTrue(response_json.get('error', '').startswith("Failed to get a valid response from AI service"))

    # Test for when Perplexity response structure is completely different (e.g. choices is not a list)
    @patch('commonthread.ct_application.ml.perplexity_service.get_perplexity_chat_response')
    def test_chat_api_perplexity_very_malformed_response(self, mock_get_perplexity_chat_response):
        mock_get_perplexity_chat_response.return_value = {
            "choices": "not-a-list", # Malformed
        }

        response = self.client.post(self.chat_url, self.valid_payload, content_type='application/json')
        
        self.assertEqual(response.status_code, 500) # Internal server error
        response_json = response.json()
        self.assertTrue(response_json.get('error', '').startswith("An unexpected server error occurred while processing AI response"))

    # Test with no stories in the project (empty context)
    @patch('commonthread.ct_application.ml.perplexity_service.get_perplexity_chat_response')
    def test_chat_api_success_no_stories(self, mock_get_perplexity_chat_response):
        mock_get_perplexity_chat_response.return_value = {
            "choices": [{"message": {"content": "Mocked AI response for empty context"}}],
        }
        # Delete existing stories for this project for this test
        Story.objects.filter(proj=self.project).delete()

        response = self.client.post(self.chat_url, self.valid_payload, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json.get('reply'), "Mocked AI response for empty context")

        expected_context = "" # Empty context
        mock_get_perplexity_chat_response.assert_called_once_with(
            settings.PERPLEXITY_API_KEY,
            expected_context,
            self.valid_payload['user_message']
        )

    # Test with a POST request that is not JSON
    def test_chat_api_non_json_post(self):
        response = self.client.post(self.chat_url, data="user_message=Hello", content_type='text/plain')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertIn("Invalid JSON", response_json.get('error', ''))
        
    # Test that the view only accepts POST requests
    def test_chat_api_get_request_not_allowed(self):
        response = self.client.get(self.chat_url)
        self.assertEqual(response.status_code, 405) # Method Not Allowed
        response_json = response.json()
        self.assertIn("Method \"GET\" not allowed.", response_json.get('detail', ''))

    def test_chat_api_put_request_not_allowed(self):
        response = self.client.put(self.chat_url, self.valid_payload, content_type='application/json')
        self.assertEqual(response.status_code, 405) # Method Not Allowed
        response_json = response.json()
        self.assertIn("Method \"PUT\" not allowed.", response_json.get('detail', ''))

    def test_chat_api_delete_request_not_allowed(self):
        response = self.client.delete(self.chat_url)
        self.assertEqual(response.status_code, 405) # Method Not Allowed
        response_json = response.json()
        self.assertIn("Method \"DELETE\" not allowed.", response_json.get('detail', ''))

    # Test with a different user who does not have access to the project (if verify_user checks this)
    # This depends on how verify_user and id_searcher determine project access for the chat API.
    # The current verify_user checks based on project_id in kwargs, so if the user has a valid session
    # but the id_searcher determines they don't have 'user' level access to this project_id, it should fail.
    # Let's assume for now that any authenticated user has 'user' access to any project for chat.
    # If a more granular check is implemented in id_searcher, this test would need adjustment.
    # The current id_searcher for a project_id in kwargs calls check_project_auth, which checks OrgUser access.
    # So, we need to ensure the user is part of the org with at least 'user' rights.
    # For simplicity, the setUp user is the curator, which implies access.
    # To test this properly, one might need another user not in the org, or in the org with insufficient perms.

    # The PERPLEXITY_API_KEY needs to be set in settings for tests, or mocked if it's accessed directly
    # For now, assuming it's set. If not, tests might fail if settings.PERPLEXITY_API_KEY is None.
    # It's better to ensure it's set for tests or explicitly mock settings.PERPLEXITY_API_KEY.
    # settings.PERPLEXITY_API_KEY = "dummy_test_key" # Can be done in setUp or a test-specific settings override

    def tearDown(self):
        # Clean up any created objects if necessary, though Django's test runner handles transaction rollbacks.
        pass
