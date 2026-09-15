from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CommentListCreateView

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='tasks')

urlpatterns = [
    path('', include(router.urls)),
    path('tasks/<int:task_id>/comments/', CommentListCreateView.as_view(), name='task-comments'),
]