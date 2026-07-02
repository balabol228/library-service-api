from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from book.models import Book
from borrowing.models import Borrowing
from payment.models import Payment
import datetime


class BorrowingApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="userpassword123"
        )
        self.other_user = get_user_model().objects.create_user(
            email="other@test.com",
            password="userpassword123"
        )
        self.client.force_authenticate(self.user)

        self.book = Book.objects.create(
            title="Django for Beginners",
            author="William Vincent",
            inventory=2,
            daily_fee=1.00
        )

    def test_list_borrowings_returns_only_user_owned(self):
        Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() + datetime.timedelta(days=7),
            book=self.book,
            user=self.user
        )
        Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() + datetime.timedelta(days=5),
            book=self.book,
            user=self.other_user
        )

        url = reverse("borrowing:borrowing-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_create_borrowing_reduces_book_inventory(self):
        url = reverse("borrowing:borrowing-list")
        payload = {
            "book": self.book.id,
            "expected_return_date": str(datetime.date.today() + datetime.timedelta(days=7))
        }
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 1)

    def test_create_borrowing_fails_if_user_has_unpaid_payments(self):
        borrowing = Borrowing.objects.create(
            borrow_date=datetime.date.today() - datetime.timedelta(days=5),
            expected_return_date=datetime.date.today() - datetime.timedelta(days=1),
            book=self.book,
            user=self.user
        )

        Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=borrowing,
            session_url="https://stripe.com/test-session",
            session_id="cs_test_12345",
            amount=5.00
        )

        url = reverse("borrowing:borrowing-list")
        payload = {
            "book": self.book.id,
            "expected_return_date": str(datetime.date.today() + datetime.timedelta(days=5))
        }
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
