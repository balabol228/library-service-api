from datetime import date
from django.core.management.base import BaseCommand
from borrowing.models import Borrowing
from borrowing.notifications import send_telegram_message


class Command(BaseCommand):
    help = "Checks for overdue borrowings and notifies admins via Telegram"

    def handle(self, *args, **options):
        today = date.today()
        
        # Шукаємо протерміновані замовлення
        overdue_borrowings = Borrowing.objects.filter(
            actual_return_date__isnull=True,
            expected_return_date__lt=today
        ).select_related("user", "book")

        if not overdue_borrowings.exists():
            # Якщо боржників немає — відправляємо стандартне повідомлення
            send_telegram_message("🟢 <b>No borrowings overdue today!</b>")
            self.stdout.write(self.style.SUCCESS("No overdue borrowings found."))
            return

        # Якщо боржники є — формуємо одне велике гарне повідомлення
        message = "⚠️ <b>Overdue Borrowings List:</b>\n\n"
        
        for borrowing in overdue_borrowings:
            overdue_days = (today - borrowing.expected_return_date).days
            message += (
                f"👤 <b>User:</b> {borrowing.user.email}\n"
                f"📚 <b>Book:</b> '{borrowing.book.title}'\n"
                f"📅 <b>Expected Return:</b> {borrowing.expected_return_date}\n"
                f"⏳ <b>Overdue by:</b> {overdue_days} days\n"
                f"-----------------------------------\n"
            )

        # Надсилаємо сформований список у Телеграм
        send_telegram_message(message)
        self.stdout.write(self.style.SUCCESS(f"Notified about {overdue_borrowings.count()} overdue borrowings."))
