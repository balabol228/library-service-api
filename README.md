# Library Service API

A robust and fully automated web API for managing book borrowings, tracking payments via Stripe, and user accounts. Designed to optimize library operations and prevent lost books.

## 🚀 Features

- **User Management**: Secure registration and JWT-based authentication.
- **Book Catalog**: Full CRUD for books (accessible to admins, read-only for regular users).
- **Borrowing System**: 
  - Borrow books with inventory validation.
  - Strict validation policy: prevents borrowing new books if the user has active unpaid borrowings or overdue fines.
- **Stripe Integration**: Automated payment session creation for initial borrowings and calculating overdue fines upon return.
- **Telegram Notifications**: 
  - Real-time alerts for new borrowings. Check out our live bot: @mate_academy_test_bot
  - Automated daily background checks that notify admins about overdue books and specific borrowers.
- **Interactive API Documentation**: Full API schema visualized with Swagger UI.

## 🛠️ Tech Stack

- **Backend**: Python 3.12, Django, Django REST Framework (DRF)
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose
- **Payment Processing**: Stripe API
- **Notifications**: Telegram Bot API
- **Documentation**: drf-spectacular (Swagger UI)

## 💻 Setup & Installation

Follow these steps to run the project locally using Docker:

### 1. Clone the Repository
```bash
git clone [https://github.com/balabol228/library-service-api.git](https://github.com/balabol228/library-service-api.git)
cd library-service-api

2. Configure Environment Variables
Create a .env file in the root directory and add your credentials:

Фрагмент коду
DJANGO_SECRET_KEY=your_django_secret_key
DEBUG=True

POSTGRES_DB=library_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

STRIPE_SECRET_KEY=your_stripe_private_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
3. Build and Run Container Environment
Bash
docker compose up --build -d
4. Run Migrations
Bash
docker compose exec web python manage.py migrate
5. Create Admin (Superuser) Account
Bash
docker compose exec web python manage.py createsuperuser
📊 API Documentation
Once the services are up and running, you can access the interactive Swagger documentation to test the endpoints:
👉 http://127.0.0.1:8080/api/doc/swagger/

⏰ Automated Tasks
To manually trigger the daily background check for overdue borrowings and send Telegram alerts, run:

Bash
docker compose exec web python manage.py check_overdue

---

superuser:
Email: admin@admin.com
password: admin123