from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "type", "borrowing", "amount", "session_id")
    list_filter = ("status", "type")
    search_fields = ("session_id", "borrowing__user__email")
