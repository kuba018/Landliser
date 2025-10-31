import pytest
from django.contrib.auth import get_user_model
pytestmark = [pytest.mark.django_db, pytest.mark.smoke]
User = get_user_model()

def test_create_user_ok():
    user = User.objects.create_user(
        username="janek",
        email="janek@example.com",
        password="TajneHaslo!123"
    )
    assert user.username == "janek"
    assert user.email == "janek@example.com"
    assert user.is_active is True
    assert user.check_password("TajneHaslo!123")

def test_create_superuser_flags():
    admin = User.objects.create_superuser(
        username="root",
        email="root@example.com",
        password="Admin!234"
    )
    assert admin.is_superuser is True
    assert admin.is_staff is True
