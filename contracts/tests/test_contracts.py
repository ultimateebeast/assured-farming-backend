import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from marketplace.models import Crop, Listing
from contracts.models import Contract, EscrowTransaction
from django.utils import timezone


@pytest.mark.django_db
def test_contract_proposal_and_escrow_flow():
    User = get_user_model()
    buyer = User.objects.create_user('buyer2', password='pass1234', role='buyer')
    farmer = User.objects.create_user('farmer2', password='pass1234', role='farmer')
    crop = Crop.objects.create(name='Maize')
    listing = Listing.objects.create(farmer=farmer, crop=crop, quantity_available=100, harvest_date=timezone.now().date(), price_floor=20)

    client = APIClient()
    client.force_authenticate(buyer)
    url = reverse('contract-list')
    data = {
        'listing_id': listing.id,
        'agreed_quantity': 10,
        'price_per_unit': '25.00',
    }
    r = client.post(url, data, format='json')
    assert r.status_code == 201
    contract_id = r.data['id']

    # create proposal
    proposal_url = reverse('contract-propose-price', args=[contract_id])
    r2 = client.post(proposal_url, {'price_per_unit': '24.00', 'message': 'offer'}, format='json')
    assert r2.status_code == 201

    # accept proposal (simulate farmer)
    client.force_authenticate(farmer)
    accept_url = reverse('contract-accept-proposal', args=[contract_id])
    proposal_id = r2.data['id']
    r3 = client.post(accept_url, {'proposal_id': proposal_id}, format='json')
    assert r3.status_code == 200

    contract = Contract.objects.get(pk=contract_id)
    assert contract.status == 'accepted'
    assert hasattr(contract, 'escrow')
    assert contract.escrow.status == 'held'
