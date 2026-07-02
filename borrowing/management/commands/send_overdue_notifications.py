import datetime
from django.core.management.base import BaseCommand
from borrowing.models import Borrowing
from borrowing.notifications import send_telegram_message


class Command(BaseCommand):
    help = "Find overdue borrowings and send a list to Telegram"

    def handle(self, *args, **options):
        today = datetime.date.today()

        overdue_borrowings = Borrowing.objects.filter(
            expected_return_date__lte=today,
            actual_return_date__isnull=True
        ).select_related("book", "user")

        if not overdue_borrowings.exists():
            send_telegram_message("🙏 <b>No borrowings overdue today!</b>")
            self.stdout.write(self.style.SUCCESS("No overdue borrowings found."))
            return

        message = "⚠️ <b>List of Overdue Borrowings:</b>\n\n"
        
        for borrowing in overdue_borrowings:
            days_overdue = (today - borrowing.expected_return_date).days
            message += (
                f"👤 <b>User:</b> {borrowing.user.email}\n"
                f"📚 <b>Book:</b> '{borrowing.book.title}'\n"
                f"📅 <b>Expected Return:</b> {borrowing.expected_return_date}\n"
                f"⏳ <b>Overdue for:</b> {days_overdue} days\n"
                f"-----------------------\n"
            )

        send_telegram_message(message)
        self.stdout.write(self.style.SUCCESS("Overdue notifications sent to Telegram."))
