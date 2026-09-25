import secrets

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterEmployeeSerializer,
    UserSerializer,
)
from django.db.models import Count, Q

from tasks.models import TaskStatus


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_manager


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by("full_name")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsManager],
        url_path="register",
    )
    def register_employee(self, request):
        """POST /api/users/register/ — регистрация сотрудника руководителем."""
        serializer = RegisterEmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        generated_password = secrets.token_urlsafe(8)
        user = serializer.save(role=CustomUser.Role.EMPLOYEE)
        user.set_password(generated_password)
        user.save()

        return Response(
            {
                "id": user.id,
                "phone": user.phone,
                "full_name": user.full_name,
                "position": user.position,
                "generated_password": generated_password,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """GET /api/users/me/ — текущий пользователь."""
        return Response(UserSerializer(request.user).data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsManager],
        url_path="busy",
    )
    def busy_employees(self, request):
        """GET /api/users/busy/ — сотрудники, отсортированные по числу активных задач."""

        employees = (
            CustomUser.objects.filter(role=CustomUser.Role.EMPLOYEE)
            .annotate(
                active_tasks=Count(
                    "assigned_tasks",
                    filter=~Q(assigned_tasks__status=TaskStatus.DONE),
                )
            )
            .order_by("-active_tasks", "full_name")
        )

        data = [
            {
                "id": emp.id,
                "full_name": emp.full_name,
                "position": emp.position,
                "phone": emp.phone,
                "active_tasks": emp.active_tasks,
            }
            for emp in employees
        ]
        return Response(data)
