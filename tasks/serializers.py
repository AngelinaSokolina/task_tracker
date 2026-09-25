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
    Смена статуса задачи сотрудником.
    Сотрудник может поставить только:
      - in_progress (взять в работу)
      - done (выполнено)
      - not_taken (отказаться, комментарий обязателен)
    Статус pending (в ожидании) — технический, вручную не ставится.
    """

    comment = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
    )

    class Meta:
        model = Task
        fields = ["status", "comment"]

    def validate_status(self, value):
        allowed = [
            TaskStatus.IN_PROGRESS,
            TaskStatus.DONE,
            TaskStatus.NOT_TAKEN,
        ]
        if value not in allowed:
            raise serializers.ValidationError(
                "Можно поставить только один из статусов: " "in_progress, done, not_taken."
            )
        return value

    def validate(self, attrs):
        new_status = attrs.get("status")
        comment = attrs.get("comment")

        if new_status == TaskStatus.NOT_TAKEN and not comment:
            raise serializers.ValidationError({"comment": "При отказе от задачи нужно указать причину в комментарии."})
        return attrs
