import pytest

pytestmark = pytest.mark.django_db

@pytest.mark.django_db 
def test_math(): #This test will create a db connection
    assert 1 == 1, "If this fails math is wrong"

# def test_math_fail(): #This test will not use a db connection
#     assert 1 == 2, "If this fails math is not wrong"


