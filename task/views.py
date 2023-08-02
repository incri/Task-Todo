import csv

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Task
from .serializers import CSVUploadSerializer, TaskSerializer
from .filters import TaskFilter


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    parser_classes = (MultiPartParser,)
    filterset_class = TaskFilter

    search_fields = ["name", "description"]
    ordering_fields = [
        "id",
        "name",
        "description",
        "is_completed",
        "priority",
        "updated_at",
    ]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        self.perform_destroy(task)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="update-completed")
    def update_completed(self, request, pk=None):
        task = self.get_object()
        serializer = TaskSerializer(
            task,
            data={"is_completed": request.data.get("is_completed")},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="csv-import")
    def bulk_create_from_csv(self, request, *args, **kwargs):
        serializer = CSVUploadSerializer(data=request.FILES)
        serializer.is_valid(raise_exception=True)

        csv_file = serializer.validated_data["csv_file"]

        tasks_to_create = []
        try:
            decoded_file = csv_file.read().decode("utf-8")
            csv_reader = csv.DictReader(decoded_file.splitlines())
            for row in csv_reader:
                tasks_to_create.append(
                    Task(
                        name=row["Name"],
                        description=row["Description"],
                        priority=row["Priority"],
                        is_completed=row["Completed"],
                        user=self.request.user,
                    )
                )

            Task.objects.bulk_create(tasks_to_create)

            return Response(
                {"message": "Tasks created successfully"},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"], url_path="csv-export")
    def export_to_csv(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="tasks.csv"'

        header = ["Id", "Name", "Description", "Priority", "Completed"]
        writer = csv.writer(response)
        writer.writerow(header)

        for task in queryset:
            writer.writerow(
                [
                    task.id,
                    task.name,
                    task.description,
                    task.priority,
                    task.is_completed,
                ]
            )

        return response
    
    
