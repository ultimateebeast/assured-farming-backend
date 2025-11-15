"""Analytics models and views for farmer metrics."""
from django.db import models
from django.conf import settings


class FarmerMetric(models.Model):
    """Snapshot of farmer metrics for reporting."""
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='metrics')
    active_contracts = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    completed_contracts = models.IntegerField(default=0)
    avg_time_to_delivery_days = models.IntegerField(null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"FarmerMetric({self.farmer.username}, {self.recorded_at})"
