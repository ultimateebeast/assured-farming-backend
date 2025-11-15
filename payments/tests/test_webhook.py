"""Webhook integration tests and escrow release tests."""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from marketplace.models import Crop, Listing
from contracts.models import Contract, PriceProposal, EscrowTransaction
from payments.models import WebhookEvent
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
def test_webhook_idempotency():
    """Test that posting the same event twice is idempotent."""
    buyer = User.objects.create_user('buyer3', password='pass1234', role='buyer')
    farmer = User.objects.create_user('farmer3', password='pass1234', role='farmer')
    crop = Crop.objects.create(name='Rice')
    listing = Listing.objects.create(
        farmer=farmer, crop=crop, quantity_available=100, harvest_date=timezone.now().date(), price_floor=20
    )
    contract = Contract.objects.create(
        listing=listing, buyer=buyer, agreed_quantity=10, price_per_unit=25, total_value=250
    )
    escrow = EscrowTransaction.objects.create(
        contract=contract, amount=250, status='held', payment_reference='mock_test_123'
    )

    client = APIClient()
    url = reverse('payments-mock-webhook')
    payload = {
        'event_id': 'test_event_001',
        'payment_reference': 'mock_test_123',
        'status': 'released',
    }

    # First call
    r1 = client.post(url, payload, format='json')
    assert r1.status_code == 200
    escrow.refresh_from_db()
    assert escrow.status == 'released'

    # Second call with same event_id (should be idempotent)
    r2 = client.post(url, payload, format='json')
    assert r2.status_code == 200
    assert r2.data['detail'] == 'Already processed'

    # Verify only one WebhookEvent was created
    assert WebhookEvent.objects.filter(event_id='test_event_001').count() == 1


@pytest.mark.django_db
def test_escrow_release_via_webhook():
    """Test that escrow transitions through states via webhook."""
    buyer = User.objects.create_user('buyer4', password='pass1234', role='buyer')
    farmer = User.objects.create_user('farmer4', password='pass1234', role='farmer')
    crop = Crop.objects.create(name='Wheat')
    listing = Listing.objects.create(
        farmer=farmer, crop=crop, quantity_available=50, harvest_date=timezone.now().date(), price_floor=30
    )
    contract = Contract.objects.create(
        listing=listing, buyer=buyer, agreed_quantity=5, price_per_unit=32, total_value=160
    )
    escrow = EscrowTransaction.objects.create(
        contract=contract, amount=160, status='pending', payment_reference='mock_release_test'
    )

    client = APIClient()
    webhook_url = reverse('payments-mock-webhook')

    # Transition pending -> held
    r1 = client.post(webhook_url, {
        'event_id': 'evt_held_001',
        'payment_reference': 'mock_release_test',
        'status': 'held'
    }, format='json')
    assert r1.status_code == 200
    escrow.refresh_from_db()
    assert escrow.status == 'held'

    # Transition held -> released
    r2 = client.post(webhook_url, {
        'event_id': 'evt_released_001',
        'payment_reference': 'mock_release_test',
        'status': 'released'
    }, format='json')
    assert r2.status_code == 200
    escrow.refresh_from_db()
    assert escrow.status == 'released'
