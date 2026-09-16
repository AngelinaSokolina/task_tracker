from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentListCreateView, TaskViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="tasks")

urlpatterns = [
    path("", include(router.urls)),
    path("tasks/<int:task_id>/comments/", CommentListCreateView.as_view(), name="task-comments"),
]
