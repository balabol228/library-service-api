from rest_framework import serializers
from book.models import Book
from .models import Borrowing
from payment.models import Payment
from rest_framework import serializers

class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )
        read_only_fields = ("id", "borrow_date", "actual_return_date", "user")

    def validate(self, attrs):
        user = self.context["request"].user

        has_pending_payments = Payment.objects.filter(
            borrowing__user=user,
            status=Payment.StatusChoices.PENDING
        ).exists()
        
        if has_pending_payments:
            raise serializers.ValidationError(
                "You have unpaid borrowings or fines. Please pay them before borrowing a new book."
            )
            
        return attrs


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.SlugRelatedField(slug_field="title", read_only=True)
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)


class BorrowingDetailSerializer(BorrowingSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta(BorrowingSerializer.Meta):
        fields = BorrowingSerializer.Meta.fields + ("book_title", "user_email")


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "book", "expected_return_date")

    def validate(self, attrs):
        data = super().validate(attrs)
        book = attrs["book"]

        if book.inventory == 0:
            raise serializers.ValidationError(
                {"book": "This book is currently out of stock."}
            )
        return data
