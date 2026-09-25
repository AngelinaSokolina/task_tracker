from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.models import Task, TaskStatus, TaskType
from users.models import CustomUser


class TaskAPITests(APITestCase):
    def setUp(self):
        self.manager = CustomUser.objects.create_user(
            phone="+79990000000",
            password="pass",
            full_name="Руководитель",
            role=CustomUser.Role.MANAGER,
        )
        self.other_manager = CustomUser.objects.create_user(
            phone="+79990000099",
            password="pass",
            full_name="Другой Руководитель",
            role=CustomUser.Role.MANAGER,
        )
        self.employee = CustomUser.objects.create_user(
            phone="+79991111111",
            password="pass",
            full_name="Сотрудник",
            role=CustomUser.Role.EMPLOYEE,
        )
        self.other_employee = CustomUser.objects.create_user(
            phone="+79992222222",
            password="pass",
            full_name="Другой Сотрудник",
            role=CustomUser.Role.EMPLOYEE,
        )

        self.task_for_employee = Task.objects.create(
            title="Задача для сотрудника",
            type=TaskType.URGENT,
            assignee=self.employee,
            author=self.manager,
            date=date(2026, 9, 15),
            status=TaskStatus.IN_PROGRESS,
        )
        self.task_for_other = Task.objects.create(
            title="Задача для другого",
            type=TaskType.DAILY,
            assignee=self.other_employee,
            author=self.manager,
            date=date(2026, 9, 15),
            status=TaskStatus.IN_PROGRESS,
        )

    def test_anonymous_cannot_list_tasks(self):
        response = self.client.get(reverse("tasks-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manager_sees_all_tasks(self):
        self.client.force_authenticate(self.manager)
        response = self.client.get(reverse("tasks-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_employee_sees_only_own_tasks(self):
        self.client.force_authenticate(self.employee)
        response = self.client.get(reverse("tasks-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.task_for_employee.id)

    def test_manager_can_create_task(self):
        self.client.force_authenticate(self.manager)
        response = self.client.post(
            reverse("tasks-list"),
            {
                "title": "Новая задача",
                "description": "Описание",
                "type": "info",
                "assignee": self.employee.id,
                "date": "2026-10-01",
                "status": "in_progress",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author_name"], "Руководитель")
        self.assertEqual(response.data["assignee_name"], "Сотрудник")

    def test_employee_cannot_create_task(self):
        self.client.force_authenticate(self.employee)
        response = self.client.post(
            reverse("tasks-list"),
            {
                "title": "X",
                "type": "daily",
                "assignee": self.employee.id,
                "date": "2026-10-01",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_can_set_status(self):
        self.client.force_authenticate(self.employee)
        url = reverse("tasks-set-status", args=[self.task_for_employee.id])
        response = self.client.patch(url, {"status": "done"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task_for_employee.refresh_from_db()
        self.assertEqual(self.task_for_employee.status, TaskStatus.DONE)

    def test_filter_by_type(self):
        self.client.force_authenticate(self.manager)
        response = self.client.get(reverse("tasks-list"), {"type": "urgent"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_date(self):
        self.client.force_authenticate(self.manager)
        response = self.client.get(reverse("tasks-list"), {"date": "2026-09-15"})
        self.assertEqual(len(response.data), 2)

    def test_filter_by_status(self):
        self.client.force_authenticate(self.manager)
        response = self.client.get(reverse("tasks-list"), {"status": "in_progress"})
        self.assertEqual(len(response.data), 2)

    def test_manager_can_delete_task(self):
        self.client.force_authenticate(self.manager)
        url = reverse("tasks-detail", args=[self.task_for_employee.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CommentAPITests(APITestCase):
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
            date=date(2026, 9, 15),
            status=TaskStatus.IN_PROGRESS,
        )

    def test_add_comment(self):
        self.client.force_authenticate(self.employee)
        url = reverse("task-comments", args=[self.task.id])
        response = self.client.post(url, {"text": "Готово"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author_name"], "Сотрудник")

    def test_list_comments(self):
        self.client.force_authenticate(self.employee)
        url = reverse("task-comments", args=[self.task.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_cannot_comment(self):
        url = reverse("task-comments", args=[self.task.id])
        response = self.client.post(url, {"text": "X"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
