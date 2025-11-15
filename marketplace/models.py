from django.db import models
from django.conf import settings
from django.utils import timezone


class Crop(models.Model):
    name = models.CharField(max_length=128)
    variety = models.CharField(max_length=128, blank=True)
    unit = models.CharField(max_length=32, default='kg')
    typical_price_range = models.CharField(max_length=64, blank=True)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.name} ({self.variety})"


class Listing(models.Model):
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='listings')
    quantity_available = models.DecimalField(max_digits=12, decimal_places=3)
    harvest_date = models.DateField()
    quality_grade = models.CharField(max_length=32, blank=True)
    location = models.CharField(max_length=255, blank=True)
    price_floor = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [models.Index(fields=['crop', 'location', 'harvest_date'])]

    def clean(self) -> None:
        # simple validation: quantity positive, harvest date not in past
        from django.core.exceptions import ValidationError

        if self.quantity_available <= 0:
            raise ValidationError('Quantity must be positive')
        if self.harvest_date < timezone.now().date():
            raise ValidationError('Harvest date cannot be in the past')

    def __str__(self) -> str:
        return f"Listing {self.pk} - {self.crop.name} by {self.farmer.username}"
