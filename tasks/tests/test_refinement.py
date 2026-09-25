from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.models import Task, TaskStatus, TaskType
from users.models import CustomUser


class ParentTaskTests(APITestCase):
    """Тесты родительских задач."""

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

    def test_create_task_with_parent(self):
        parent = Task.objects.create(
            title="Родитель",
            type=TaskType.URGENT,
            assignee=self.employee,
            author=self.manager,
            date=date.today(),
        )
        self.client.force_authenticate(self.manager)
        response = self.client.post(
            reverse("tasks-list"),
            {
                "title": "Подзадача",
                "type": "daily",
                "assignee": self.employee.id,
                "date": str(date.today()),
                "parent": parent.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["parent"], parent.id)

    def test_new_task_default_status_pending(self):
        self.client.force_authenticate(self.manager)
        response = self.client.post(
            reverse("tasks-list"),
            {
                "title": "Новая",
                "type": "daily",
                "assignee": self.employee.id,
                "date": str(date.today()),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "pending")

    def test_subtasks_count(self):
        parent = Task.objects.create(
            title="Родитель",
            type=TaskType.URGENT,
            assignee=self.employee,
            author=self.manager,
            date=date.today(),
        )
        for i in range(2):
            Task.objects.create(
                title=f"Подзадача {i}",
                type=TaskType.DAILY,
                assignee=self.employee,
                author=self.manager,
                date=date.today(),
                parent=parent,
            )
        self.client.force_authenticate(self.manager)
        response = self.client.get(reverse("tasks-detail", args=[parent.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["subtasks_count"], 2)


class StatusWithCommentTests(APITestCase):
    """Тесты смены статуса с комментарием."""

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
        self.task = Task.objects.create(
            title="Задача",
            type=TaskType.URGENT,
            assignee=self.employee,
            author=self.manager,
            date=date.today(),
            status=TaskStatus.IN_PROGRESS,
        )

    def test_set_status_done_without_comment(self):
        self.client.force_authenticate(self.employee)
        url = reverse("tasks-set-status", args=[self.task.id])
        response = self.client.patch(url, {"status": "done"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, TaskStatus.DONE)

    def test_set_pending_without_comment_fails(self):
        self.client.force_authenticate(self.employee)
        url = reverse("tasks-set-status", args=[self.task.id])
        response = self.client.patch(url, {"status": "pending"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("comment", response.data)

    def test_set_pending_with_comment_creates_comment(self):
        self.client.force_authenticate(self.employee)
        url = reverse("tasks-set-status", args=[self.task.id])
        response = self.client.patch(
            url,
            {
                "status": "pending",
                "comment": "Загружен другой задачей",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, TaskStatus.PENDING)
        self.assertEqual(self.task.comments.count(), 1)
        self.assertEqual(self.task.comments.first().author, self.employee)


class BusyEmployeesTests(APITestCase):
    """Тесты эндпоинта /api/users/busy/."""

    def setUp(self):
        self.manager = CustomUser.objects.create_user(
            phone="+79990000000",
            password="pass",
            full_name="Руководитель",
            role=CustomUser.Role.MANAGER,
        )
        self.employee1 = CustomUser.objects.create_user(
            phone="+79991111111",
            password="pass",
            full_name="Занят",
            role=CustomUser.Role.EMPLOYEE,
        )
        self.employee2 = CustomUser.objects.create_user(
            phone="+79992222222",
            password="pass",
            full_name="Свободен",
            role=CustomUser.Role.EMPLOYEE,
        )
        # employee1 — 2 активные задачи
        for i in range(2):
            Task.objects.create(
                title=f"Задача {i}",
                type=TaskType.DAILY,
                assignee=self.employee1,
                author=self.manager,
                date=date.today(),
            )
        # employee2 — только выполненная (не считается)
        Task.objects.create(
            title="Готово",
            type=TaskType.DAILY,
            assignee=self.employee2,
            author=self.manager,
            date=date.today(),
            status=TaskStatus.DONE,
        )

    def test_busy_sorted_by_active_tasks(self):
        self.client.force_authenticate(self.manager)
        response = self.client.get(reverse("users-busy-employees"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["phone"], "+79991111111")
        self.assertEqual(response.data[0]["active_tasks"], 2)

    def test_employee_cannot_access_busy(self):
        self.client.force_authenticate(self.employee1)
        response = self.client.get(reverse("users-busy-employees"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_access_busy(self):
        response = self.client.get(reverse("users-busy-employees"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ImportantTasksTests(APITestCase):
    """Тесты эндпоинта /api/tasks/important/."""

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
        self.other = CustomUser.objects.create_user(
            phone="+79992222222",
            password="pass",
            full_name="Другой",
            role=CustomUser.Role.EMPLOYEE,
        )
        # Срочная задача для employee
        Task.objects.create(
            title="Срочная",
            type=TaskType.URGENT,
            assignee=self.employee,
            author=self.manager,
            date=date.today(),
        )
        # Просроченная задача для other
        Task.objects.create(
            title="Просрочка",
            type=TaskType.DAILY,
            assignee=self.other,
            author=self.manager,
            date=date.today() - timedelta(days=3),
        )
        # Обычная будущая — не важная
        Task.objects.create(
            title="Обычная",
            type=TaskType.INFO,
            assignee=self.employee,
            author=self.manager,
            date=date.today() + timedelta(days=5),
        )
        # Выполненная срочная — не важная
        Task.objects.create(
            title="Готово",
            type=TaskType.URGENT,
            assignee=self.employee,
            author=self.manager,
            date=date.today(),
            status=TaskStatus.DONE,
        )

    def test_manager_sees_all_important(self):
        self.client.force_authenticate(self.manager)
        response = self.client.get(reverse("tasks-important"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["tasks"]), 2)
        self.assertIn("suggested_assignees", response.data)

    def test_employee_sees_only_own_important(self):
        self.client.force_authenticate(self.employee)
        response = self.client.get(reverse("tasks-important"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Только своя срочная
        self.assertEqual(len(response.data["tasks"]), 1)
        self.assertNotIn("suggested_assignees", response.data)

    def test_anonymous_cannot_access(self):
        response = self.client.get(reverse("tasks-important"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
