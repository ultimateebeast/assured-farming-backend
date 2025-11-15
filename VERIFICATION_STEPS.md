# Quick Verification Steps

## Prerequisites

- Docker & Docker Compose installed
- Working internet connection (for pulling images)
- ~5 minutes

## Step-by-Step Testing

### 1. Start the Project

```bash
cd assured_farming
docker-compose up --build
```

Wait for output: `INFO: Application startup complete` (indicates web service ready)

### 2. In Another Terminal: Run Migrations

```bash
docker-compose exec web python manage.py migrate
```

Expected output: All migrations applied for accounts, marketplace, contracts, payments, analytics, notifications

### 3. Create a Superuser

```bash
docker-compose exec web python manage.py createsuperuser
# Follow the prompts - example:
# Username: admin
# Email: admin@example.com
# Password: admin123
```

### 4. Seed Demo Data

```bash
docker-compose exec web python manage.py seed_demo_data
```

Expected output: Sample users, crops, and listings created

### 5. Run the Test Suite

```bash
docker-compose exec web pytest -v
```

Expected test results:

- ✅ `test_accounts::test_user_registration` - Basic user registration
- ✅ `test_contracts::test_contract_creation` - Contract creation flow
- ✅ `test_contracts::test_escrow_creation` - Escrow created on proposal acceptance
- ✅ `test_webhook::test_webhook_idempotency` - Webhook handles duplicate events
- ✅ `test_webhook::test_escrow_status_transitions` - Escrow status updates on webhook

### 6. Check API Endpoints

**Get JWT Token:**

```bash
curl -X POST http://localhost:8000/api/v1/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"farmer1","password":"password123"}'
```

Response should include `access` and `refresh` tokens.

**List Crops:**

```bash
curl http://localhost:8000/api/v1/marketplace/crops/
```

**List Listings:**

```bash
curl http://localhost:8000/api/v1/marketplace/listings/
```

### 7. Access Web Interfaces

- **Django Admin:** http://localhost:8000/admin/ (username: admin, password from step 3)
- **API Docs (Swagger):** http://localhost:8000/api/v1/schema/swagger-ui/
- **Admin Dashboard:** http://localhost:8000/admin/dashboard/ (shows pending KYCs, disputes, contracts)

### 8. Stop Services

```bash
docker-compose down
```

---

## Expected Success Indicators

✅ All services start without errors
✅ Migrations complete without issues
✅ Django admin loads
✅ API endpoints respond with 200 status
✅ Tests pass (4-5 tests depending on test selection)
✅ Swagger UI shows all endpoints
✅ Admin dashboard displays (even if empty after migrations)

---

## Troubleshooting

### Port Already in Use (8000, 5432, 6379)

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use docker-compose with different port:
docker-compose -f docker-compose.yml up --build -p 8001:8000
```

### Database Connection Error

```bash
# Wait longer for postgres to start
docker-compose logs db

# Then retry migrations
docker-compose exec web python manage.py migrate
```

### Celery Tasks Not Running

```bash
# Check celery worker is running
docker-compose logs celery

# Tasks are enqueued but may run async. Check Redis:
docker-compose exec redis redis-cli KEYS '*'
```

### Import Errors in Docker

```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## What Each Component Tests

| Test                       | Purpose                                   | Status   |
| -------------------------- | ----------------------------------------- | -------- |
| `test_user_registration`   | User creation and profile creation        | ✅ Works |
| `test_contract_creation`   | Contract workflow (draft → proposed)      | ✅ Works |
| `test_escrow_creation`     | Escrow created when proposal accepted     | ✅ Works |
| `test_webhook_idempotency` | Same event_id returns "Already processed" | ✅ Works |
| `test_escrow_transitions`  | Escrow status changes on webhook          | ✅ Works |

---

## Next Steps After Verification

If all tests pass:

1. Expand test coverage (PDF generation, analytics queries)
2. Integrate real payment provider (Stripe)
3. Add real email/SMS provider
4. Build React frontend consuming these endpoints
5. Deploy to production environment

If tests fail:

1. Check logs: `docker-compose logs <service_name>`
2. Verify migrations: `docker-compose exec web python manage.py showmigrations`
3. Check database: `docker-compose exec db psql -U postgres -d assured_farming -l`
4. Review error messages and traceback
