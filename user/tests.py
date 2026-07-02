from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class UserApiTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("user:create")
        self.me_url = reverse("user:manage")
        self.user_data = {
            "email": "testuser@example.com",
            "password": "TestPassword123",
        }

    def test_create_user_success(self):
        # Test successful user registration
        res = self.client.post(self.register_url, self.user_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("email", res.data)
        self.assertEqual(res.data["email"], self.user_data["email"])
        self.assertNotIn("password", res.data)  # Password should be write-only

    def test_get_profile_unauthenticated_forbidden(self):
        # Unauthenticated user cannot access profile data
        res = self.client.get(self.me_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_authenticated_success(self):
        # Authenticated user can successfully get their own profile data
        user = get_user_model().objects.create_user(**self.user_data)
        self.client.force_authenticate(user)
        
        res = self.client.get(self.me_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], user.email)
