from django.db import models


class SMSLog(models.Model):
    to = models.CharField(max_length=64)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"SMS to {self.to} at {self.sent_at}"
