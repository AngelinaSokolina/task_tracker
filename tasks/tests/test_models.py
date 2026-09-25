from datetime import date

from django.test import TestCase

from tasks.models import Comment, Task, TaskStatus, TaskType
from users.models import CustomUser


class TaskModelTests(TestCase):
    def setUp(self):
        self.manager = CustomUser.objects.create_user(
            phone="+79990000000",
            password="pass",
            full_name="Руководитель",
            role=CustomUser.Role.MANAGER,
        )
        self.employee = CustomUser.objects.create_user(
            phone="+79991111111",
            password="pass",
            full_name="Сотрудник",
            role=CustomUser.Role.EMPLOYEE,
        )

    def test_create_task(self):
        task = Task.objects.create(
            title="Задача",
            description="Описание",
            type=TaskType.URGENT,
            assignee=self.employee,
            author=self.manager,
            date=date(2026, 9, 15),
        )
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.type, TaskType.URGENT)
        self.assertEqual(str(task), "Срочная: Задача")

    def test_create_comment(self):
        task = Task.objects.create(
            title="Задача",
            type=TaskType.INFO,
            assignee=self.employee,
            author=self.manager,
            date=date(2026, 9, 15),
        )
        comment = Comment.objects.create(task=task, author=self.employee, text="Готово")
        self.assertEqual(comment.text, "Готово")
        self.assertEqual(task.comments.count(), 1)

    def test_task_ordering(self):
        """Задачи сортируются по убыванию даты."""
        Task.objects.create(
            title="Старая",
            type=TaskType.DAILY,
            assignee=self.employee,
            author=self.manager,
            date=date(2026, 9, 1),
        )
        t2 = Task.objects.create(
            title="Новая",
            type=TaskType.DAILY,
            assignee=self.employee,
            author=self.manager,
            date=date(2026, 9, 20),
        )
        first = Task.objects.first()
        self.assertEqual(first, t2)
