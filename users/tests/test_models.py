from django.test import TestCase

from users.models import CustomUser


class CustomUserModelTests(TestCase):
    """Тесты модели CustomUser."""

    def test_create_user_with_phone(self):
        user = CustomUser.objects.create_user(
            phone="+79990000000",
            password="pass12345",
            full_name="Тест",
        )
        self.assertEqual(user.phone, "+79990000000")
        self.assertTrue(user.check_password("pass12345"))
        self.assertEqual(user.role, CustomUser.Role.EMPLOYEE)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        user = CustomUser.objects.create_superuser(
            phone="+79990000001",
            password="pass12345",
            full_name="Админ",
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, CustomUser.Role.MANAGER)

    def test_str_representation(self):
        user = CustomUser.objects.create_user(
            phone="+79990000002",
            password="pass12345",
            full_name="Иванов Иван",
        )
        self.assertEqual(str(user), "Иванов Иван (+79990000002)")

    def test_is_manager_property(self):
        manager = CustomUser.objects.create_user(
            phone="+79990000003",
            password="pass12345",
            full_name="М",
            role=CustomUser.Role.MANAGER,
        )
        employee = CustomUser.objects.create_user(
            phone="+79990000004",
            password="pass12345",
            full_name="С",
            role=CustomUser.Role.EMPLOYEE,
        )
        self.assertTrue(manager.is_manager)
        self.assertFalse(manager.is_employee)
        self.assertTrue(employee.is_employee)
        self.assertFalse(employee.is_manager)

    def test_create_user_without_phone_raises(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(phone="", password="x", full_name="X")
