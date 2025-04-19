from django.test import TestCase

#import backend.tests as bt
#import frontend.tests as ft

# Create your tests here.

# Sample Test: To be moved to different folder on proof of concept
class PageViewTests(TestCase):
    '''
    Class for testing status codes & outputs for templates/views for the frontend
    '''
    def math_test(self):
        self.assertEqual(200, 200)

    def homepage_test(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)