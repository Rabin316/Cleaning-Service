# Clean Pro - Professional Cleaning Service Platform

A production-ready Django web application for booking professional cleaning services online. Features a comprehensive customer portal, admin dashboard, and integrated payment processing.

## 🚀 Features

### Customer Features
- **Service Catalog**: Browse and book various cleaning services
- **Booking System**: Schedule one-time or recurring cleanings (weekly, bi-weekly, monthly)
- **Customer Accounts**: Registration, login, and profile management
- **Saved Addresses**: Store multiple addresses for quick booking
- **Favorite Services**: Quickly rebook preferred services
- **Dashboard**: View upcoming bookings, booking history, and statistics
- **Notifications**: In-app notifications for booking updates
- **Payment History**: View past payments and receipts
- **Reviews**: Rate and review completed services
- **Mobile Responsive**: Fully responsive design for all devices

### Operational Features (Admin)
- **Operations Dashboard**: Real-time metrics (bookings, revenue, team status)
- **Team Management**: Assign bookings to team members, view schedules
- **Booking Management**: Full CRUD operations with bulk actions
- **Service Management**: Create/edit services with pricing and features
- **Revenue Reports**: Financial analytics with interactive charts
- **Team Schedule View**: Visual weekly schedule for all team members
- **Testimonial Management**: Approve/reject customer testimonials
- **Export Capabilities**: Export bookings to CSV

### Payment Features
- **Stripe Integration**: Secure payment processing with PCI compliance
- **Payment Webhooks**: Automatic payment status updates
- **Multiple Payment Statuses**: Pending, paid, failed, refunded
- **Secure**: Uses Stripe Elements for PCI-compliant card collection

### Technical Features
- **Environment-based Configuration**: Uses environment variables for secrets
- **Docker Ready**: Full Docker and docker-compose setup
- **Nginx Configuration**: Production-ready reverse proxy config
- **Health Checks**: Built-in health check endpoint
- **Structured Logging**: JSON logging for production debugging
- **Security Headers**: HSTS, XSS protection, content security policy
- **Static File Optimization**: WhiteNoise for production static serving

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL 12+ (recommended, or SQLite for development)
- Redis (for Celery, optional for background tasks)
- Stripe Account (for payment processing)

## 🔧 Installation

### Quick Start (Development)

```bash
# Clone the repository
git clone <repository-url>
cd cleaning-service

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows Command Prompt:
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your development settings

# Apply database migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

On Windows, run the commands above after activating `venv`. If PowerShell execution
policy prevents activation, use the virtual-environment interpreter directly:

```powershell
$env:DEBUG = "True"
$env:SECRET_KEY = "local-development-key"
$env:ALLOWED_HOSTS = "127.0.0.1,localhost"
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py runserver
```

### Docker Deployment

```bash
# Create .env file
cp .env.example .env
# Edit .env with your production settings

# Start all services
docker-compose up -d --build

# Apply database migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following:

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key for sessions and CSRF | Yes |
| `DEBUG` | Set to `False` in production | No (defaults to False) |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | Yes |
| `DATABASE_URL` | Database connection string | Yes (PostgreSQL recommended) |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | Yes (for payments) |
| `STRIPE_SECRET_KEY` | Stripe secret key | Yes (for payments) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | Yes (for webhooks) |
| `EMAIL_HOST` | SMTP server host | For production email |
| `EMAIL_PORT` | SMTP server port | For production email |
| `EMAIL_HOST_USER` | SMTP username | For production email |
| `EMAIL_HOST_PASSWORD` | SMTP password | For production email |

### Stripe Setup

1. Create a Stripe account at [stripe.com](https://stripe.com)
2. Get your API keys from the Stripe Dashboard
3. Set up Webhooks in Stripe Dashboard with endpoint: `https://yourdomain.com/webhook/stripe/`
4. Add the webhook signing secret to `STRIPE_WEBHOOK_SECRET`

## 🏗️ Project Structure

```
.
├── cleaning/
│   ├── migrations/          # Database migrations
│   ├── templates/           # HTML templates
│   │   ├── admin/           # Custom admin templates
│   │   └── cleaning/        # Main app templates
│   ├── static/              # Static files (CSS, JS, images)
│   ├── admin.py             # Admin configuration
│   ├── models.py            # Database models
│   ├── forms.py             # Form definitions
│   ├── views.py             # Main views
│   ├── urls.py              # URL routing
│   └── stripe_utils.py      # Stripe payment utilities
├── config/
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── health.py            # Health check views
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker orchestration
├── nginx.conf               # Nginx reverse proxy config
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
└── manage.py                # Django management script
```

## 🎮 Usage

### Development Mode

In DEBUG mode, the application:
- Uses SQLite database (no external database required)
- Uses console email backend (emails printed to console)
- Automatically marks test bookings as paid
- Loads Stripe.js but uses test mode

### Production Mode

In production mode:
- Requires PostgreSQL or MySQL database
- Uses SMTP for email delivery
- Processes real Stripe payments
- Enforces HTTPS
- Implements security headers (HSTS, XSS protection, etc.)

## 📊 Admin Dashboard

Access the admin dashboard at `/admin/dashboard/`:

- **Key Metrics**: Total bookings, pending/confirmed counts, revenue
- **Today's Schedule**: Upcoming bookings for the current day
- **Recent Activity**: Latest bookings and status changes
- **Popular Services**: Most requested services ranked
- **Team Schedule**: Visual weekly schedule for all team members
- **Revenue Reports**: Financial analytics with interactive charts

## 🎯 API Endpoints

### Public Pages
- `/` - Home page
- `/services/` - Service catalog
- `/services/{slug}/` - Service detail page
- `/booking/` - Booking form (with Stripe integration)
- `/about/` - About page
- `/contact/` - Contact form

### Authentication
- `/register/` - Customer registration
- `/login/` - Customer login
- `/logout/` - Customer logout

### Customer Dashboard (requires login)
- `/dashboard/` - Dashboard overview
- `/dashboard/bookings/` - All bookings
- `/dashboard/booking/{id}/` - Booking details
- `/dashboard/profile/` - Profile management
- `/dashboard/addresses/` - Saved addresses
- `/dashboard/favorites/` - Favorite services
- `/dashboard/notifications/` - Notification center
- `/dashboard/payments/` - Payment history

### Admin
- `/admin/` - Admin panel
- `/admin/dashboard/` - Operations dashboard
- `/admin/dashboard/revenue/` - Revenue reports
- `/admin/dashboard/team-schedule/` - Team scheduling

### Payment Processing
- `/webhook/stripe/` - Stripe webhook endpoint
- `/payment/success/` - Payment success redirect
- `/payment/failed/` - Payment failed redirect

## 🔒 Security Features

- Environment-based secret management
- CSRF protection on all forms
- Secure cookie settings in production
- HSTS (HTTP Strict Transport Security)
- XSS protection headers
- Content Security Policy
- Clickjacking protection
- Secure password validation

## 🧪 Testing

Run tests:
```bash
python manage.py test
```

## 🐳 Docker Deployment

### Development

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### Production

1. Set up SSL certificates (Let's Encrypt recommended)
2. Configure environment variables in `.env`
3. Build and deploy:
```bash
docker-compose -f docker-compose.yml up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

## 📝 License

This project is proprietary software. All rights reserved.

## 👥 Contributing

For questions or support, contact the development team.

## 🚨 Troubleshooting

### Payment Issues

- Verify Stripe API keys are set correctly in `.env`
- Check Stripe webhook endpoint is configured correctly
- Enable webhook signing in Stripe Dashboard

### Docker Issues

- Ensure Docker and docker-compose are installed
- Check `.env` file exists and is configured
- Verify ports 80, 443, 5432, 6379 are available

### Database Issues

- Ensure PostgreSQL connection string is valid in `DATABASE_URL`
- Run migrations: `python manage.py migrate`
- For production, use PostgreSQL (not SQLite)

## 📞 Support

For support and questions, please contact:
- Email: info@cleanpro.com
- Phone: +1 (555) 123-4567

---

Built with ❤️ using Django 6.0, Stripe, and Docker.