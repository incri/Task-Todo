from rest_framework.test import APIClient

from django.contrib.auth.models import User

import pytest


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticate_user(api_client):
    def do_authenticate_user():
        user = User.objects.create_user(
            id=1, username="testuser", password="testpassword"
        )
        api_client.force_authenticate(user=user)
        return user

    return do_authenticate_user
