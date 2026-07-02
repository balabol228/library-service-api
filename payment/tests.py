from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from book.models import Book
from borrowing.models import Borrowing
from payment.models import Payment
import datetime


class PaymentApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="client@test.com", password="password123"
        )
        self.other_user = get_user_model().objects.create_user(
            email="other_client@test.com", password="password123"
        )
        self.client.force_authenticate(self.user)

        self.book = Book.objects.create(
            title="Test Book", author="Author", inventory=5, daily_fee=1.00
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() + datetime.timedelta(days=3),
            book=self.book,
            user=self.user
        )

    def test_list_payments_returns_only_user_owned_payments(self):
        Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=self.borrowing,
            session_url="https://stripe.com/test",
            session_id="session_123",
            amount=3.00
        )
        
        other_borrowing = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() + datetime.timedelta(days=3),
            book=self.book,
            user=self.other_user
        )
        Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=other_borrowing,
            session_url="https://stripe.com/test2",
            session_id="session_456",
            amount=3.00
        )

        url = reverse("payment:payment-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
