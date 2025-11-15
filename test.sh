#!/bin/bash
# Test script for Assured Farming project
# Run this after docker-compose is up and healthy

set -e

echo "=== Assured Farming Test Suite ==="
echo ""

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run migrations
echo "📦 Running migrations..."
docker-compose exec -T web python manage.py migrate --noinput

# Create superuser (for testing)
echo "👤 Creating test superuser..."
docker-compose exec -T web python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("✓ Admin user created")
else:
    print("✓ Admin user already exists")
EOF

# Seed demo data
echo "🌱 Seeding demo data..."
docker-compose exec -T web python manage.py seed_demo_data

# Run pytest
echo ""
echo "🧪 Running tests..."
docker-compose exec -T web pytest -v --tb=short

echo ""
echo "✅ Test suite complete!"
