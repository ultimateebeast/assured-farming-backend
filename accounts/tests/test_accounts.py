import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_and_me_flow():
    client = APIClient()
    url = reverse('api-register')
    data = {
        'username': 'farmer1',
        'email': 'farmer1@example.com',
        'password': 'pass1234',
        'role': 'farmer'
    }
    r = client.post(url, data, format='json')
    assert r.status_code == 201
    # login with credentials using token endpoint
