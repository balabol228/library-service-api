from datetime import date
from django.db import transaction
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingListSerializer
from .notifications import send_telegram_message
from payment.stripe_session import create_stripe_fine_session


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        from payment.stripe_session import create_stripe_session
        
        with transaction.atomic():
            borrowing = serializer.save(user=self.request.user)
            book = borrowing.book
            book.inventory -= 1
            book.save()
            payment = create_stripe_session(borrowing, self.request)

        message = (
            f"🔔 <b>New Borrowing Created!</b>\n\n"
            f"👤 <b>User:</b> {borrowing.user.email}\n"
            f"📚 <b>Book:</b> {book.title}\n"
            f"💰 <b>Amount:</b> ${payment.amount}\n"
            f"💳 <a href='{payment.session_url}'><b>Click here to Pay</b></a>"
        )
        send_telegram_message(message)

    @action(detail=True, methods=["POST"], url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            return Response(
                {"error": "This borrowing has already been returned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            today = date.today()
            borrowing.actual_return_date = today
            borrowing.save()

            book = borrowing.book
            book.inventory += 1
            book.save()

        if today > borrowing.expected_return_date:
            overdue_days = (today - borrowing.expected_return_date).days

            fine_payment = create_stripe_fine_session(borrowing, overdue_days, request)

            message = (
                f"⚠️ <b>Book Returned LATE! Fine Issued.</b>\n\n"
                f"👤 <b>User:</b> {borrowing.user.email}\n"
                f"📚 <b>Book:</b> {book.title}\n"
                f"⏳ <b>Overdue Days:</b> {overdue_days}\n"
                f"💰 <b>Fine Amount:</b> ${fine_payment.amount}\n"
                f"💳 <a href='{fine_payment.session_url}'><b>Pay Fine Here</b></a>"
            )
            send_telegram_message(message)

            return Response(
                {
                    "message": "Book returned, but it was overdue! A fine has been issued.",
                    "fine_amount": fine_payment.amount,
                    "payment_url": fine_payment.session_url
                },
                status=status.HTTP_200_OK
            )

        message = (
            f"🟢 <b>Book Returned on Time!</b>\n\n"
            f"👤 <b>User:</b> {borrowing.user.email}\n"
            f"📚 <b>Book:</b> {book.title}"
        )
        send_telegram_message(message)

        return Response(
            {"message": "Book returned successfully on time!"}, 
            status=status.HTTP_200_OK
        )
