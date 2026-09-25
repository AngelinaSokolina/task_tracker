from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Comment, Task, TaskStatus, TaskType
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
        """
        PATCH /api/tasks/{id}/status/ — смена статуса задачи.
        Если статус = pending (не взята в работу) — нужен комментарий с причиной.
        """
        task = self.get_object()
        serializer = TaskStatusUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        comment_text = serializer.validated_data.pop("comment", None)
        serializer.save()

        if comment_text:
            Comment.objects.create(
                task=task,
                author=request.user,
                text=comment_text,
            )

        return Response(TaskSerializer(task).data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="important",
    )
    def important(self, request):
        """
        GET /api/tasks/important/ — важные задачи (срочные и просроченные).
        Руководителю — с подбором свободных исполнителей.
        """
        from datetime import date

        from django.db.models import Count, Q

        from users.models import CustomUser

        user = request.user
        today = date.today()

        urgent = (
            Task.objects.filter(type=TaskType.URGENT)
            .exclude(status=TaskStatus.DONE)
            .select_related("assignee", "author")
            .prefetch_related("comments")
        )
        overdue = (
            Task.objects.filter(date__lt=today)
            .exclude(status=TaskStatus.DONE)
            .select_related("assignee", "author")
            .prefetch_related("comments")
        )
        qs = (urgent | overdue).distinct().order_by("date")

        if not user.is_manager:
            qs = qs.filter(assignee=user)

        result = {"tasks": TaskSerializer(qs, many=True).data}

        if user.is_manager:
            free = (
                CustomUser.objects.filter(role=CustomUser.Role.EMPLOYEE)
                .annotate(
                    active=Count(
                        "assigned_tasks",
                        filter=~Q(assigned_tasks__status=TaskStatus.DONE),
                    )
                )
                .order_by("active", "full_name")[:5]
            )
            result["suggested_assignees"] = [
                {
                    "id": u.id,
                    "full_name": u.full_name,
                    "active_tasks": u.active,
                }
                for u in free
            ]

        return Response(result)


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs["task_id"]).select_related("author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, task_id=self.kwargs["task_id"])
