import uuid
from typing import Dict

def create_mock_charge(contract, amount: float) -> Dict[str, str]:
    """Simulate creating a payment charge and return a payment reference.

    In a real integration, this would call Stripe/other provider and return a charge id or session id.
    """
    payment_reference = f"mock_{uuid.uuid4().hex}"
    # In a real implementation, you'd persist a pending payment or return a checkout URL.
    return {
        'payment_reference': payment_reference,
        'status': 'created',
        'amount': amount,
    }

