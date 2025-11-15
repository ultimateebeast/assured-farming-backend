from celery import shared_task
from django.db import transaction
from contracts.models import EscrowTransaction


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def release_escrow_task(self, escrow_id: int):
    """Release escrow if conditions met. Called after delivery confirmation or timeout."""
    try:
        with transaction.atomic():
            escrow = EscrowTransaction.objects.select_for_update().get(pk=escrow_id)
            if escrow.status in ('released', 'refunded'):
                return 'already_finalized'
            escrow.status = 'released'
            escrow.save()
            return 'released'
    except EscrowTransaction.DoesNotExist:
        return 'not_found'
