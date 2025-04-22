from django.test import TestCase, SimpleTestCase


class ModelTests(TestCase):

    def test_math(self):
        assert 1 == 1, "If this fails math is wrong"

    def test_math_fail(self):
        assert 1 == 2, "If this fails math is not wrong"