import pytest
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]

def test_register_201_when_valid():
    client = APIClient()
    payload = {
        "username": "testuser",
        "email": "test@landliser.com",
        "password": "StrongPass!123"
    }
    url = reverse("user-register")
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 201

def test_jwt_login_and_access_protected():
    client = APIClient()
    # najpierw rejestracja, żeby było kogo logować
    client.post(reverse("user-register"), {
        "username": "jwtuser",
        "email": "jwt@landliser.com",
        "password": "TokenPass!321"
    }, format="json")

    resp = client.post(reverse("token_obtain_pair"), {
        "username": "jwtuser",
        "password": "TokenPass!321"
    }, format="json")
    assert resp.status_code == 200
    access = resp.data.get("access")
    assert access

    # uderzamy w chroniony endpoint
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    protected_url = reverse("user-me")
    ping = client.get(protected_url)
    assert ping.status_code in (200, 204)  # 200 jeśli zwracasz dane, 204 jeśli pusto
