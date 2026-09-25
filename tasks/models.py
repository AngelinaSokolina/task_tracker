from django.conf import settings
from django.db import models


class TaskType(models.TextChoices):
    URGENT = "urgent", "Срочная"
    DAILY = "daily", "Повседневная"
    INFO = "info", "Информационная"


class TaskStatus(models.TextChoices):
    PENDING = "pending", "Не взята в работу"
    IN_PROGRESS = "in_progress", "В процессе"
    DONE = "done", "Выполнено"


class Task(models.Model):
    """
    Задача, которую руководитель ставит сотруднику.
    Отображается точкой на календаре:
      - красная  — urgent
      - синяя    — daily
      - зелёная  — info
    """

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Комментарий")

    type = models.CharField(
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.DAILY,
        verbose_name="Степень задачи",
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_tasks",
        verbose_name="Исполнитель",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks",
        verbose_name="Отправитель",
    )

    date = models.DateField(verbose_name="Дата задачи")

    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
        verbose_name="Статус",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subtasks",
        verbose_name="Родительская задача",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.get_type_display()}: {self.title}"


class Comment(models.Model):
    """
    Комментарий к задаче. Показывается в карточке задачи.
    """

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Задача",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    text = models.TextField(verbose_name="Текст")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]

    def __str__(self):
        return f"Комментарий от {self.author} к задаче #{self.task_id}"
