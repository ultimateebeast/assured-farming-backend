from celery import shared_task
from django.core.mail import send_mail


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, event_type: str, payload: dict):
    # Very small mock: map event types to subjects. In production use templates and provider.
    subject_map = {
        'proposal_created': 'New price proposal',
        'proposal_accepted': 'Proposal accepted',
        'contract_signed': 'Contract signed',
        'shipment_delivered': 'Shipment delivered',
    }
    subject = subject_map.get(event_type, 'Notification')
    try:
        send_mail(subject, str(payload), 'no-reply@assuredfarming.example', ['admin@localhost'])
    except Exception as exc:
        raise self.retry(exc=exc)

