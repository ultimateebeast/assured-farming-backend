"""
ASSURED FARMING - QUICK REFERENCE GUIDE
Copy-paste commands for testing, development, and deployment
"""

# ==============================================================================

# 1. LOCAL DEVELOPMENT (DOCKER)

# ==============================================================================

## Start all services (web, db, redis, celery, celery-beat)

docker-compose up --build

## In a new terminal - Run migrations

docker-compose exec web python manage.py migrate

## Create superuser

docker-compose exec web python manage.py createsuperuser

## Seed demo data (sample users, crops, listings)

docker-compose exec web python manage.py seed_demo_data

## Run all tests

docker-compose exec web pytest -v

## Run specific test file

docker-compose exec web pytest payments/tests/test_webhook.py -v

## Run with coverage report

docker-compose exec web pytest --cov=accounts --cov=contracts --cov=payments --cov-report=html

## Check migrations

docker-compose exec web python manage.py showmigrations

## Make new migrations after model changes

docker-compose exec web python manage.py makemigrations

## Interactive shell (like Django shell)

docker-compose exec web python manage.py shell

## View logs

docker-compose logs -f web # Django app
docker-compose logs -f db # PostgreSQL
docker-compose logs -f redis # Redis
docker-compose logs -f celery # Celery worker

## Stop services

docker-compose down

## Stop and remove volumes (clean slate)

docker-compose down -v

---

# ==============================================================================

# 2. LOCAL DEVELOPMENT (WITHOUT DOCKER - Manual Setup)

# ==============================================================================

## Create virtual environment

python -m venv venv

## Activate virtual environment (Windows)

venv\Scripts\activate

## Activate virtual environment (Mac/Linux)

source venv/bin/activate

## Install dependencies

pip install -r requirements-prod.txt

## Copy environment file

cp .env.example .env

## Run migrations (assumes PostgreSQL and Redis running locally)

python manage.py migrate

## Create superuser

python manage.py createsuperuser

## Seed demo data

python manage.py seed_demo_data

## Start development server (http://localhost:8000)

python manage.py runserver

## In another terminal - start Celery worker

celery -A assured_farming worker -l info

## In another terminal - start Celery Beat scheduler

celery -A assured_farming beat -l info

## Run tests

pytest -v

---

# ==============================================================================

# 3. API TESTING (CURL)

# ==============================================================================

## Get JWT token

curl -X POST http://localhost:8000/api/v1/accounts/token/ \
 -H "Content-Type: application/json" \
 -d '{"username":"farmer1","password":"password123"}'

# Response: {"access":"<TOKEN>","refresh":"<REFRESH_TOKEN>"}

## Use token for authenticated requests (replace TOKEN)

curl -H "Authorization: Bearer <TOKEN>" \
 http://localhost:8000/api/v1/accounts/me/

## List crops (no auth needed)

curl http://localhost:8000/api/v1/marketplace/crops/

## List listings with filters

curl "http://localhost:8000/api/v1/marketplace/listings/?crop=1&location=Lagos"

## Create listing (requires farmer role and token)

curl -X POST http://localhost:8000/api/v1/marketplace/listings/ \
 -H "Authorization: Bearer <TOKEN>" \
 -H "Content-Type: application/json" \
 -d '{
"crop": 1,
"quantity": 100,
"harvest_date": "2024-12-25",
"quality_grade": "A",
"location": "Lagos",
"price_floor": 5000
}'

## Create contract (requires buyer token)

curl -X POST http://localhost:8000/api/v1/contracts/contracts/ \
 -H "Authorization: Bearer <TOKEN>" \
 -H "Content-Type: application/json" \
 -d '{"listing": 1}'

## Propose price

curl -X POST http://localhost:8000/api/v1/contracts/contracts/1/propose-price/ \
 -H "Authorization: Bearer <TOKEN>" \
 -H "Content-Type: application/json" \
 -d '{"proposed_price": 5500}'

## Accept proposal (creates escrow)

curl -X POST http://localhost:8000/api/v1/contracts/contracts/1/accept-proposal/ \
 -H "Authorization: Bearer <TOKEN>" \
 -H "Content-Type: application/json" \
 -d '{"proposal_id": 1}'

## Get farmer analytics

curl -H "Authorization: Bearer <TOKEN>" \
 http://localhost:8000/api/v1/analytics/farmer-revenue/

## Send test webhook

curl -X POST http://localhost:8000/api/v1/payments/mock/webhook/ \
 -H "Content-Type: application/json" \
 -d '{
"event_id": "event_123",
"payment_reference": "mock_abc123",
"status": "completed"
}'

---

# ==============================================================================

# 4. WEB INTERFACES (BROWSER)

# ==============================================================================

## Django Admin

http://localhost:8000/admin/

# Login with superuser credentials (created via createsuperuser)

## API Documentation (Swagger UI)

http://localhost:8000/api/v1/schema/swagger-ui/

## Admin Dashboard (pending KYCs, disputes, contracts)

http://localhost:8000/admin/dashboard/

## Raw Schema (OpenAPI 3.0 JSON)

http://localhost:8000/api/v1/schema/

---

# ==============================================================================

# 5. USEFUL QUERIES & DEBUGGING

# ==============================================================================

## Check database connection

docker-compose exec db psql -U postgres -d assured_farming -c "SELECT 1"

## Connect to PostgreSQL shell

docker-compose exec db psql -U postgres -d assured_farming

## Inside psql shell:

# List all tables

\dt

# View table schema

\d accounts_user

# Count records

SELECT COUNT(\*) FROM accounts_user;

# Exit

\q

## Connect to Redis

docker-compose exec redis redis-cli

## Inside redis CLI:

# List all keys

KEYS \*

# Get value

GET <key>

# Delete key

DEL <key>

# Flush all (careful!)

FLUSHALL

# Exit

EXIT

## Check running migrations

docker-compose exec web python manage.py showmigrations

## Rollback migration

docker-compose exec web python manage.py migrate accounts 0000

## Create empty migration (for custom SQL)

docker-compose exec web python manage.py makemigrations --empty accounts --name custom_migration

---

# ==============================================================================

# 6. COMMON TROUBLESHOOTING

# ==============================================================================

## Port 8000 already in use

# Kill the process

lsof -ti:8000 | xargs kill -9

# Or use different port

docker-compose up --build -p 8001:8000

## Database connection errors

# Ensure postgres is running

docker-compose ps

# Check postgres logs

docker-compose logs db

# Restart postgres

docker-compose restart db

## Celery tasks not running

# Check celery worker is running

docker-compose ps celery

# Check Redis connection

docker-compose exec redis redis-cli ping

# Response: PONG

# Check Celery logs

docker-compose logs celery

## Import errors after code changes

# Rebuild containers

docker-compose down
docker-compose build --no-cache
docker-compose up

## Migrations not detected

# Check migrations folder exists

ls -la contracts/migrations/

# Create **init**.py if missing

touch contracts/migrations/**init**.py

# Recreate migrations

docker-compose exec web python manage.py makemigrations

---

# ==============================================================================

# 7. PRODUCTION DEPLOYMENT

# ==============================================================================

## Update environment variables

# Copy .env.example to .env and fill in production values

cp .env.example .env

# Edit .env with production settings

## Key production env vars to update

DJANGO_SECRET_KEY=<generate-new-secret>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
POSTGRES_HOST=production-db-host
POSTGRES_PASSWORD=<strong-password>
REDIS_URL=redis://production-redis-host:6379/0

## Build production image

docker build -t assured-farming:latest .

## Push to registry (Docker Hub example)

docker tag assured-farming:latest yourregistry/assured-farming:latest
docker push yourregistry/assured-farming:latest

## Deploy on Docker Compose (VPS/Server)

# Transfer docker-compose.yml and .env

scp docker-compose.yml user@server:/app/
scp .env user@server:/app/

# SSH into server and start

ssh user@server
cd /app
docker-compose pull
docker-compose up -d

# Run migrations on server

docker-compose exec web python manage.py migrate

# Create superuser on server

docker-compose exec web python manage.py createsuperuser

---

# ==============================================================================

# 8. PERFORMANCE & MONITORING

# ==============================================================================

## Check slow queries

docker-compose exec web python manage.py debugsqlshell

## Monitor Celery tasks

# Open new terminal with celery flower

docker-compose run --rm -p 5555:5555 celery celery -A assured_farming flower

# Access at http://localhost:5555

## Profile view execution

# Add to settings.py (development only):

MIDDLEWARE += ['django.middleware.cache.UpdateCacheMiddleware']
CACHES = {
'default': {
'BACKEND': 'django.core.cache.backends.redis.RedisCache',
'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
}
}

---

# ==============================================================================

# 9. BACKUP & RESTORE

# ==============================================================================

## Backup PostgreSQL database

docker-compose exec db pg_dump -U postgres assured_farming > backup.sql

## Restore from backup

docker-compose exec db psql -U postgres assured_farming < backup.sql

## Backup media files (contract PDFs, KYC documents)

docker cp $(docker-compose ps -q web):/app/media ./media_backup

---

# ==============================================================================

# 10. USEFUL DJANGO COMMANDS

# ==============================================================================

## Check for issues

docker-compose exec web python manage.py check

## Collect static files (if configured)

docker-compose exec web python manage.py collectstatic --noinput

## Clear cache

docker-compose exec web python manage.py clear_cache

## Export data

docker-compose exec web python manage.py dumpdata --format json > data.json

## Import data

docker-compose exec web python manage.py loaddata data.json

## Flush database (CAREFUL!)

docker-compose exec web python manage.py flush

---

# ==============================================================================

# 11. GIT WORKFLOW

# ==============================================================================

## Initialize git repo

git init
git add .
git commit -m "Initial assured farming project"

## Create new branch for feature

git checkout -b feature/new-feature

## Make changes and commit

git add .
git commit -m "Add new feature"

## Push to remote

git push origin feature/new-feature

## Create pull request (on GitHub)

# Go to https://github.com/yourrepo/pulls

## Merge to main

git checkout main
git pull origin main
git merge feature/new-feature
git push origin main

---

# ==============================================================================

# 12. HELPFUL REFERENCES

# ==============================================================================

## Project Documentation

- README.md ...................... Quick start
- README_EXTENDED.md ............. Comprehensive docs
- PROJECT_SUMMARY.md ............ Completion status
- VERIFICATION_STEPS.md ......... Testing guide
- COMPLETION_CHECKLIST.md ....... Feature checklist

## API Endpoints

- Swagger UI ........... http://localhost:8000/api/v1/schema/swagger-ui/
- OpenAPI Schema ....... http://localhost:8000/api/v1/schema/
- README_EXTENDED.md ... Lists all 30+ endpoints

## Key Files

- Django Settings ......... assured_farming/settings.py
- Project URLs ........... assured_farming/urls.py
- Celery Config .......... assured_farming/celery.py
- Requirements ........... requirements-prod.txt
- Environment Template ... .env.example

## Useful Aliases (add to .bashrc or .zshrc)

alias dcup="docker-compose up --build"
alias dcdown="docker-compose down"
alias dclog="docker-compose logs -f"
alias dcexec="docker-compose exec web"
alias dctest="docker-compose exec web pytest"
alias dcmigrate="docker-compose exec web python manage.py migrate"
alias dcseed="docker-compose exec web python manage.py seed_demo_data"

---

## END OF QUICK REFERENCE

Save this file locally for quick copy-paste access during development.
Last updated: Current session
Version: 1.0 - Production Ready
