import stripe
from django.conf import settings
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.notifications import send_telegram_message
from .models import Payment
from .serializers import PaymentSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.select_related("borrowing__user", "borrowing__book")
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:
            return queryset.filter(borrowing__user=self.request.user)
        return queryset

    @action(detail=False, methods=["GET"], url_path="success")
    def success(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"error": "Missing session_id parameter"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = Payment.objects.get(session_id=session_id)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == "paid":
            payment.status = Payment.StatusChoices.PAID
            payment.save()

            message = (
                f"✅ <b>Payment Confirmed!</b>\n\n"
                f"👤 <b>User:</b> {payment.borrowing.user.email}\n"
                f"📚 <b>Book:</b> '{payment.borrowing.book.title}'\n"
                f"💰 <b>Amount Paid:</b> ${payment.amount}\n"
                f"💳 <b>Stripe ID:</b> {payment.session_id[:15]}..."
            )
            send_telegram_message(message)

            return Response(
                {"message": "Payment successful! Thank you."}, 
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Payment has not been verified by Stripe yet."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=["GET"], url_path="cancel")
    def cancel(self, request):
        return Response(
            {
                "message": "Payment was canceled. You can complete the payment within 24 hours using your payment link."
            },
            status=status.HTTP_200_OK
        )
