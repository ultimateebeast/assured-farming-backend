from django.db import models


class WebhookEvent(models.Model):
    """Records processed webhook event ids for idempotency."""
    event_id = models.CharField(max_length=255, unique=True)
    payload = models.JSONField(default=dict)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"WebhookEvent({self.event_id})"
