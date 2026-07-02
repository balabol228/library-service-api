from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from book.models import Book


class PublicBookApiTests(APITestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Clean Code",
            author="Robert Martin",
            inventory=5,
            daily_fee=2.00
        )

    def test_list_books_allowed_for_anonymous_user(self):
        url = reverse("book:book-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_book_forbidden_for_anonymous_user(self):
        url = reverse("book:book-list")
        payload = {
            "title": "Refactoring",
            "author": "Martin Fowler",
            "inventory": 3,
            "daily_fee": 1.50
        }
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminBookApiTests(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@test.com",
            password="adminpassword123"
        )
        self.client.force_authenticate(self.admin_user)
        self.book = Book.objects.create(
            title="Clean Code",
            author="Robert Martin",
            inventory=5,
            daily_fee=2.00
        )

    def test_create_book_allowed_for_admin(self):
        url = reverse("book:book-list")
        payload = {
            "title": "Refactoring",
            "author": "Martin Fowler",
            "inventory": 3,
            "daily_fee": 1.50
        }
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
