from rest_framework.routers import DefaultRouter


from django.urls import path, include
from . import views

router = DefaultRouter()
router.register("tasks", views.TaskViewSet, basename="tasks")

urlpatterns = router.urls
