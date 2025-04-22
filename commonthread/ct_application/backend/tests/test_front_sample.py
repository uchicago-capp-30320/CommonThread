from django.test import TestCase, SimpleTestCase


class PageViewTests(SimpleTestCase):
    #Class for testing status codes & outputs for templates/views for the frontend
    def test_math(self):
        assert 1 == 1, "If this fails math is wrong"

    def test_homepage(self):
        response = self.client.get('/')
        assert response.status_code == 200, "Page did not return 200 status code"