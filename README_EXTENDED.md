"""Extended README with complete setup, endpoints, and workflow examples."""

# Assured Farming - Contract Farming System

A production-grade Django + DRF backend for contract farming with escrow payments, KYC verification, price negotiation, and analytics.

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (if running locally without Docker)

### Run Locally with Docker

1. **Clone and setup environment:**

   ```bash
   cd assured_farming
   cp .env.example .env
   # Edit .env if needed (defaults work for local dev)
   ```

2. **Build and start services:**

   ```bash
   docker-compose up --build
   ```

3. **Create superuser (in new terminal):**

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Seed demo data:**

   ```bash
   docker-compose exec web python manage.py seed_demo_data
   ```

5. **Run tests:**
   ```bash
   docker-compose exec web pytest -q
   ```

### Access Points

- **API Documentation:** http://localhost:8000/api/v1/schema/swagger-ui/
- **Django Admin:** http://localhost:8000/admin/
- **Admin Dashboard:** http://localhost:8000/admin/dashboard/

## Key Features

### 1. User Management & KYC

- Farmer and Buyer registration with role-based access
- KYC document upload (file size validation)
- Admin review workflow for KYC documents

**Endpoints:**

- `POST /api/v1/accounts/register/` — Register new user
- `POST /api/v1/accounts/token/` — Obtain JWT token
- `GET /api/v1/accounts/me/` — Get current user profile
- `POST /api/v1/accounts/kyc/upload/` — Upload KYC documents

### 2. Marketplace

- Browse and list crops by farmers
- Search/filter listings by crop, location, date, quality, price
- Pagination support

**Endpoints:**

- `GET /api/v1/marketplace/crops/` — List all crops
- `POST /api/v1/marketplace/listings/` — Create listing (farmer only)
- `GET /api/v1/marketplace/listings/?search=rice&location=bihar` — Search listings
- `GET /api/v1/marketplace/listings/recent/` — Recent listings

### 3. Contracts & Negotiation

- Buyer initiates contract from listing
- Farmer and buyer exchange price proposals (offers/counteroffers)
- Accept proposal to bind contract
- E-sign contract (generates signed PDF)

**Endpoints:**

- `POST /api/v1/contracts/contracts/` — Create contract
- `POST /api/v1/contracts/contracts/{id}/propose-price/` — Make price proposal
- `POST /api/v1/contracts/contracts/{id}/accept-proposal/` — Accept proposal + create escrow
- `POST /api/v1/contracts/contracts/{id}/sign/` — Sign and e-generate PDF
- `GET /api/v1/contracts/contracts/{id}/` — Get contract details

### 4. Escrow & Payments (Mock Gateway)

- Escrow created when contract accepted
- Mock payment gateway creates "charge" reference
- Webhook endpoint to update escrow status (held, released, refunded)
- Idempotency: same `event_id` never processes twice

**Endpoints:**

- `GET /api/v1/contracts/escrows/` — List escrow transactions
- `POST /api/v1/payments/mock/webhook/` — Handle payment events
- `POST /api/v1/payments/mock/trigger/` — Simulate payment provider webhook (dev only)

**Webhook Payload Example:**

```json
{
  "event_id": "evt_12345",
  "payment_reference": "mock_abc123",
  "status": "released"
}
```

### 5. Shipment & Delivery

- Mark shipment as dispatched
- Confirm delivery (triggers escrow release)

**Endpoints:**

- `POST /api/v1/contracts/shipments/` — Create shipment
- `POST /api/v1/contracts/shipments/{id}/confirm-delivery/` — Confirm delivery

### 6. Disputes

- Raise dispute on contract
- Admin review and resolution

**Endpoints:**

- `POST /api/v1/contracts/disputes/` — Raise dispute
- `GET /api/v1/contracts/disputes/` — List disputes

### 7. Analytics (Farmer Dashboard)

- Total revenue from completed contracts
- Active contract count
- Average delivery time
- Proposal acceptance rate

**Endpoints:**

- `GET /api/v1/analytics/farmer-revenue/` — Farmer total revenue (farmer only)
- `GET /api/v1/analytics/active-contracts/` — Active contract count
- `GET /api/v1/analytics/avg-delivery-time/` — Avg days to delivery (farmer only)
- `GET /api/v1/analytics/acceptance-rate/` — Proposal acceptance rate

### 8. Notifications (Mock)

- Email notifications for key events (via Celery)
- Mock SMS provider (logged to SMSLog model for audit)

**Celery Tasks:**

- `send_email_task` — Send email notifications
- `send_sms_task` — Log SMS (mock provider)
- `generate_contract_pdf_task` — Generate signed PDF asynchronously
- `release_escrow_task` — Release escrow after delay/approval

## Workflow Example: Contract Creation & Escrow

```
1. Farmer creates listing
   POST /api/v1/marketplace/listings/
   { "crop_id": 1, "quantity_available": 100, "harvest_date": "2024-01-15", "price_floor": 20 }

2. Buyer views listing
   GET /api/v1/marketplace/listings/1/

3. Buyer creates contract
   POST /api/v1/contracts/contracts/
   { "listing_id": 1, "agreed_quantity": 50, "price_per_unit": 20 }

4. Buyer proposes initial price
   POST /api/v1/contracts/contracts/1/propose-price/
   { "price_per_unit": 19.50, "message": "Can you lower the price?" }

5. Farmer accepts proposal → Escrow created (held status)
   POST /api/v1/contracts/contracts/1/accept-proposal/
   { "proposal_id": 1 }

   → Creates EscrowTransaction with payment_reference, status='held'

6. Buyer signs contract
   POST /api/v1/contracts/contracts/1/sign/
   → Generates signed PDF (async task)
   → Contract status becomes 'active'

7. Farmer ships goods
   POST /api/v1/contracts/shipments/
   { "contract_id": 1, "pickup_date": "2024-01-10", "tracking_id": "TRACK123" }

8. Buyer confirms delivery
   POST /api/v1/contracts/shipments/1/confirm-delivery/
   { "delivery_date": "2024-01-15" }
   → Escrow transitions to 'released'
   → Funds transferred to farmer (in production)

9. Optional: Raise dispute if issues
   POST /api/v1/contracts/disputes/
   { "contract_id": 1, "description": "Received damaged goods" }
```

## Authentication

The API uses **JWT (JSON Web Token)** authentication via `djangorestframework-simplejwt`.

### Obtain Token

```bash
curl -X POST http://localhost:8000/api/v1/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "farmer1", "password": "pass1234"}'
```

Response:

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Use Token in Requests

```bash
curl http://localhost:8000/api/v1/accounts/me/ \
  -H "Authorization: Bearer <access_token>"
```

## Admin Interfaces

### Django Admin (`/admin/`)

- User management (create farmers, buyers, admins)
- KYC document review
- Contract and escrow monitoring
- Dispute resolution
- AuditLog browsing

### Admin Dashboard (`/admin/dashboard/`)

- Pending KYC approvals (quick overview)
- Open disputes
- Contracts requiring attention

## Development

### File Structure

```
assured_farming/
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── README.md
├── pytest.ini
├── assured_farming/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── core/                     # Core utilities
│   ├── middleware.py         # Request auditing
│   ├── admin_dashboard.py    # Admin dashboard views
│   └── management/commands/
│       └── seed_demo_data.py # Demo data
├── accounts/                 # User, KYC, profiles
├── marketplace/              # Crops, listings
├── contracts/                # Contracts, proposals, escrow
├── payments/                 # Mock gateway, webhooks
├── notifications/            # Email, SMS tasks
├── analytics/                # Farmer metrics
└── templates/                # HTML templates
```

### Running Tests

```bash
docker-compose exec web pytest -q
docker-compose exec web pytest contracts/tests/test_contracts.py -v
docker-compose exec web pytest payments/tests/test_webhook.py -v
```

### Running Linters

```bash
docker-compose exec web ruff check .
docker-compose exec web black --check .
docker-compose exec web isort --check .
```

### Celery Tasks

In local development, tasks run synchronously (task_always_eager = True in tests).

For async task processing (production), ensure Redis is running and start Celery:

```bash
docker-compose up celery celery-beat
```

## Security Considerations

1. **Secrets:** Store `DJANGO_SECRET_KEY`, payment keys, etc. in `.env` (never commit to repo).
2. **File Uploads:** KYC documents are validated (size/type) before storage.
3. **Auditing:** All requests logged to `AuditLog` model via middleware.
4. **Idempotency:** Webhook events are deduplicated by `event_id` using `WebhookEvent` model.
5. **Rate Limiting:** Can be added to login/KYC endpoints via DRF throttle classes (not yet configured).

## Production Deployment

### Heroku/Gunicorn Setup

```bash
# Procfile (included)
web: gunicorn assured_farming.wsgi:application --bind 0.0.0.0:$PORT

# Install gunicorn
pip install gunicorn
```

### Environment Variables (Production)

```
DJANGO_SECRET_KEY=<strong-random-key>
DJANGO_DEBUG=False
POSTGRES_DB=assured_farming_prod
POSTGRES_USER=<user>
POSTGRES_PASSWORD=<strong-password>
POSTGRES_HOST=<db-host>
REDIS_URL=redis://<redis-host>:6379/0
CELERY_BROKER_URL=redis://<redis-host>:6379/1
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<app-password>
```

## Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes and add tests
3. Run linters and tests: `docker-compose exec web pytest && ruff check .`
4. Commit: `git commit -am "Add my feature"`
5. Push: `git push origin feature/my-feature`

## Support & Documentation

- API Schema: http://localhost:8000/api/v1/schema/
- Swagger UI: http://localhost:8000/api/v1/schema/swagger-ui/
- ReDoc: http://localhost:8000/api/v1/schema/redoc/

## License

MIT
