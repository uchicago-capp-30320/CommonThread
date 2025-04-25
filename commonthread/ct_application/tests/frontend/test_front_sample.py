#import pytest # Needed for certain markings


def test_math(): # Sample test, should always succeed
        assert 1 == 1, "If this fails math is wrong"


def test_homepage(client): # Client will simulate requests
    response = client.get('/')
    assert response.status_code == 200, "Page did not return 200 status code"