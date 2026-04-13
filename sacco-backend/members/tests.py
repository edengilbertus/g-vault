from rest_framework import status
from rest_framework.test import APITestCase

from members.models import User


class AuthApiTests(APITestCase):
    def test_register_returns_token_and_user(self):
        payload = {
            "full_name": "Julian Thorne",
            "email": "julian@example.com",
            "phone_number": "+254700000001",
            "national_id": "ID-12345678",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }

        response = self.client.post("/api/auth/register/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["email"], payload["email"])
        self.assertTrue(User.objects.filter(email=payload["email"]).exists())

    def test_login_with_email_and_password(self):
        user = User.objects.create_user(
            email="member@example.com",
            password="StrongPass123!",
            full_name="Test Member",
            phone_number="+254700000002",
        )

        response = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
