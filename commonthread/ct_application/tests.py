from django.test import TestCase
from django.urls import reverse

#import backend.tests as bt
#import frontend.tests as ft

# Create your tests here.

# Sample Test: To be moved to different folder on proof of concept
class PageViewTests(TestCase):
    '''
    Class for testing status codes & outputs for templates/views for the frontend
    '''
    def homepage_test(self):
        response = self.client.get(reverse('/'))
        assert response.status_code == 200

sample_test = PageViewTests()
sample_test.homepage_test()