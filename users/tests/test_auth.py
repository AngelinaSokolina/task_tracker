from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import CustomUser


class AuthTests(APITestCase):
    """Тесты JWT-авторизации по номеру телефона."""

    def setUp(self):
        self.manager = CustomUser.objects.create_user(
            phone="+79990000000",
            password="admin12345",
            full_name="Руководитель",
            role=CustomUser.Role.MANAGER,
        )

    def test_token_obtain_success(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {
                "phone": "+79990000000",
                "password": "admin12345",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["role"], "manager")

    def test_token_obtain_wrong_password(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {
                "phone": "+79990000000",
                "password": "wrong-pass",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_obtain_wrong_phone(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {
                "phone": "+70000000000",
                "password": "admin12345",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_endpoint_returns_current_user(self):
        self.client.force_authenticate(self.manager)
        url = reverse("users-me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone"], "+79990000000")
        self.assertEqual(response.data["role"], "manager")

    def test_me_requires_auth(self):
        url = reverse("users-me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RegisterEmployeeTests(APITestCase):
    """Тесты регистрации сотрудника руководителем."""

    def setUp(self):
        self.manager = CustomUser.objects.create_user(
            phone="+79990000000",
            password="admin12345",
            full_name="Руководитель",
            role=CustomUser.Role.MANAGER,
        )
        self.employee = CustomUser.objects.create_user(
            phone="+79991111111",
            password="emp12345",
            full_name="Сотрудник",
            role=CustomUser.Role.EMPLOYEE,
        )

    def test_manager_can_register_employee(self):
        self.client.force_authenticate(self.manager)
        url = reverse("users-register-employee")
        response = self.client.post(
            url,
            {
                "phone": "+79992223344",
                "full_name": "Новый Сотрудник",
                "position": "Бухгалтер",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("generated_password", response.data)
        self.assertEqual(response.data["phone"], "+79992223344")

        new_user = CustomUser.objects.get(phone="+79992223344")
        self.assertTrue(new_user.check_password(response.data["generated_password"]))
        self.assertEqual(new_user.role, CustomUser.Role.EMPLOYEE)

    def test_employee_cannot_register(self):
        self.client.force_authenticate(self.employee)
        url = reverse("users-register-employee")
        response = self.client.post(
            url,
            {
                "phone": "+79993334455",
                "full_name": "Кто-то",
                "position": "X",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_register(self):
        url = reverse("users-register-employee")
        response = self.client.post(
            url,
            {
                "phone": "+79994445566",
                "full_name": "Кто-то",
                "position": "X",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
