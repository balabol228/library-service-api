import stripe
from django.conf import settings
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing, request) -> Payment:
    """Генерує сесію звичайної оплати при створенні замовлення"""
    duration = (borrowing.expected_return_date - borrowing.borrow_date).days
    if duration <= 0:
        duration = 1

    total_price = duration * borrowing.book.daily_fee
    stripe_amount = int(total_price * 100)
    base_url = request.build_absolute_uri("/")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": stripe_amount,
                    "product_data": {
                        "name": f"Borrowing: {borrowing.book.title}",
                        "description": f"Rent for {duration} days",
                    },
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=f"{base_url}api/payments/success/?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{base_url}api/payments/cancel/",
    )

    payment = Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=Payment.TypeChoices.PAYMENT,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        amount=total_price,
    )

    return payment


def create_stripe_fine_session(borrowing, overdue_days, request) -> Payment:
    fine_amount = overdue_days * borrowing.book.daily_fee * 2
    stripe_amount = int(fine_amount * 100)
    base_url = request.build_absolute_uri("/")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": stripe_amount,
                    "product_data": {
                        "name": f"FINE for Overdue Book: {borrowing.book.title}",
                        "description": f"Overdue by {overdue_days} days. Fine multiplier: 2x",
                    },
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=f"{base_url}api/payments/success/?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{base_url}api/payments/cancel/",
    )

    payment = Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=Payment.TypeChoices.FINE,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        amount=fine_amount,
    )

    return payment
