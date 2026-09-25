from rest_framework import serializers

from .models import Comment, Task, TaskStatus


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source="author.full_name")

    class Meta:
        model = Comment
        fields = ["id", "task", "author", "author_name", "text", "created_at"]
        read_only_fields = ["task", "author", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    assignee_name = serializers.ReadOnlyField(source="assignee.full_name")
    author_name = serializers.ReadOnlyField(source="author.full_name")
    comments = CommentSerializer(many=True, read_only=True)
    subtasks_count = serializers.IntegerField(source="subtasks.count", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "type",
            "status",
            "assignee",
            "assignee_name",
            "author",
            "author_name",
            "date",
            "created_at",
            "updated_at",
            "parent",
            "subtasks_count",
            "comments",
        ]
        read_only_fields = ["author", "created_at", "updated_at"]


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Для смены статуса сотрудником.
    Если статус = pending (не взята в работу) — комментарий с причиной обязателен.
    """

    comment = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
    )

    class Meta:
        model = Task
        fields = ["status", "comment"]

    def validate(self, attrs):
        new_status = attrs.get("status")
        comment = attrs.get("comment")

        if new_status == TaskStatus.PENDING and not comment:
            raise serializers.ValidationError(
                {"comment": "При переводе задачи в статус «Не взята в работу» " "нужно указать причину в комментарии."}
            )
        return attrs
