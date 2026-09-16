from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Comment, Task
from .serializers import (
    CommentSerializer,
    TaskSerializer,
    TaskStatusUpdateSerializer,
)


class IsManagerOrReadOnly(permissions.BasePermission):
    """Создавать/редактировать задачи может только руководитель."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.is_manager


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["date", "type", "status", "assignee"]

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.select_related("assignee", "author").prefetch_related("comments")
        # Руководитель видит все задачи, сотрудник — только свои
        if user.is_manager:
            return qs
        return qs.filter(assignee=user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["patch"], url_path="status", permission_classes=[permissions.IsAuthenticated])
    def set_status(self, request, pk=None):
        """PATCH /api/tasks/{id}/status/ — сотрудник ставит «в процессе» / «выполнено»."""
        task = self.get_object()
        serializer = TaskStatusUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TaskSerializer(task).data)


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs["task_id"]).select_related("author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, task_id=self.kwargs["task_id"])
