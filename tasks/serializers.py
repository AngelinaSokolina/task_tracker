from rest_framework import serializers
from .models import Task, Comment


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.full_name')

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'author_name', 'text', 'created_at']
        read_only_fields = ['task', 'author', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    assignee_name = serializers.ReadOnlyField(source='assignee.full_name')
    author_name = serializers.ReadOnlyField(source='author.full_name')
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description',
            'type', 'status',
            'assignee', 'assignee_name',
            'author', 'author_name',
            'date', 'created_at', 'updated_at',
            'comments',
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    """Для смены статуса сотрудником."""
    class Meta:
        model = Task
        fields = ['status']