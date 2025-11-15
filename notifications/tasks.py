"""Celery tasks for notifications: email and mock SMS."""
from celery import shared_task
from django.core.mail import send_mail
from .models import SMSLog


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_task(self, to: str, message: str):
    """Mock SMS provider: log SMS to DB instead of sending."""
    try:
        SMSLog.objects.create(to=to, message=message)
        return f'SMS logged to {to}'
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task_notification(self, subject: str, message: str, recipients: list):
    """Send email via Django mail backend."""
    try:
        send_mail(subject, message, 'no-reply@assuredfarming.example', recipients)
        return f'Email sent to {recipients}'
    except Exception as exc:
        raise self.retry(exc=exc)
