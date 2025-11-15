# Assured Farming - Contract Farming System

A production-ready Django + REST Framework backend for secure contract farming, price negotiation, escrow payments, KYC verification, and farmer analytics.

## Quick Start

```bash
cp .env.example .env
docker-compose up --build
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py seed_demo_data
docker-compose exec web pytest -q
```

## Features

✅ User registration & role-based access (Farmer / Buyer / Admin)
✅ KYC verification with document upload & admin review
✅ Crop listing & marketplace search/filter
✅ Contract negotiation with price proposals (offers/counteroffers)
✅ E-signing with PDF generation
✅ Escrow payments (mock gateway + idempotent webhooks)
✅ Shipment tracking & delivery confirmation
✅ Dispute resolution
✅ Analytics: revenue, active contracts, delivery times
✅ Email & SMS notifications (Celery tasks)
✅ Admin dashboard for pending KYCs, disputes, contracts
✅ OpenAPI schema (Swagger UI)

## Key Endpoints

**Auth & Users:**

- `POST /api/v1/accounts/register/` – Register
- `POST /api/v1/accounts/token/` – Get JWT token
- `GET /api/v1/accounts/me/` – Current user profile

**Marketplace:**

- `GET /api/v1/marketplace/listings/` – Browse listings
- `POST /api/v1/marketplace/listings/` – Create listing (farmer)

**Contracts:**

- `POST /api/v1/contracts/contracts/` – Create contract
- `POST /api/v1/contracts/contracts/{id}/propose-price/` – Make offer
- `POST /api/v1/contracts/contracts/{id}/accept-proposal/` – Accept (creates escrow)
- `POST /api/v1/contracts/contracts/{id}/sign/` – E-sign (generates PDF)

**Payments & Escrow:**

- `POST /api/v1/payments/mock/webhook/` – Handle payment callbacks (idempotent)
- `GET /api/v1/contracts/escrows/` – View escrow status

**Analytics:**

- `GET /api/v1/analytics/farmer-revenue/` – Farmer revenue
- `GET /api/v1/analytics/active-contracts/` – Active contract count

## Documentation

Full docs & workflow examples in [README_EXTENDED.md](README_EXTENDED.md).

## API Docs

- **Swagger:** http://localhost:8000/api/v1/schema/swagger-ui/
- **ReDoc:** http://localhost:8000/api/v1/schema/redoc/

## Admin

- Django Admin: http://localhost:8000/admin/
- Dashboard: http://localhost:8000/admin/dashboard/

## Tech Stack

- Python 3.11+ / Django 4.2 LTS
- PostgreSQL
- Redis + Celery (async tasks)
- DRF + SimpleJWT (API & auth)
- WeasyPrint/xhtml2pdf (PDF generation)
- Docker & docker-compose

## Testing

```bash
docker-compose exec web pytest -q              # Run all tests
docker-compose exec web pytest -v contracts/   # Run specific app tests
docker-compose exec web pytest --cov           # Coverage report
```

## Deployment

Included: `Procfile` for Heroku/Gunicorn. See full docs for production setup.

---

**For complete workflow examples, admin config, and deployment guidance, see README_EXTENDED.md.**
