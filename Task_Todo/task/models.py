from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    title = models.TextField(max_length=255)
    description = models.TextField(max_length=255)
    complete = models.BooleanField(default=False)
    priority = models.IntegerField(max_value=5, min_value=1)
    last_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")

    class Meta:
        ordering = ["last_update"]
