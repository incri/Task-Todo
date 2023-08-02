import uuid
from rest_framework import status

from django.contrib.auth.models import User

from model_bakery import baker
import pytest

from task.models import Task
from task.serializers import TaskSerializer


@pytest.fixture
def create_task(api_client):
    def do_create_task(task):
        return api_client.post("/tasks/", task)

    return do_create_task


@pytest.mark.django_db
class TestCreateTask:
    def test_if_user_is_anonymous_return_401(self, create_task):
        response = create_task({"name": "a", "description": "apple", "priority": 4})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_data_is_invalid_return_400(self, authenticate_user, create_task):
        authenticate_user()
        response = create_task({"name": ""})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["name"] is not None

    def test_if_data_is_valid_return_201(self, authenticate_user, create_task):
        authenticate_user()
        response = create_task(
            {
                "name": "a",
                "description": "apple",
                "priority": 4,
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0


@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_task_exists_return_200(self, authenticate_user, api_client):
        user = authenticate_user()

        task = baker.make(Task, user=user)

        response = api_client.get(f"/tasks/{task.id}/")

        # Assert  response
        assert response.status_code == status.HTTP_200_OK
        assert response.data == TaskSerializer(task).data
