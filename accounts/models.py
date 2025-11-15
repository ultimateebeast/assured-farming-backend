from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.contrib.postgres.indexes import GinIndex


class User(AbstractUser):
    class Roles(models.TextChoices):
        FARMER = 'farmer', _('Farmer')
        BUYER = 'buyer', _('Buyer')
        ADMIN = 'admin', _('Admin')

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.FARMER)
    phone = models.CharField(max_length=20, blank=True, null=True, validators=[RegexValidator(r'^\+?\d{7,15}$')])
    is_verified = models.BooleanField(default=False)


class AuditLog(models.Model):
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [GinIndex(fields=['metadata'])]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.timestamp.isoformat()} {self.action}"


class FarmerProfile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='farmer_profile')
    kyc_status = models.CharField(max_length=20, default='pending')
    farm_locations = models.TextField(blank=True)
    bank_details_masked = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return f"FarmerProfile({self.user.username})"


class BuyerProfile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='buyer_profile')
    company_name = models.CharField(max_length=255, blank=True)
    gst_number = models.CharField(max_length=64, blank=True)
    contact_person = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return f"BuyerProfile({self.user.username})"


class KYCDocument(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='kyc_documents')
    document = models.FileField(upload_to='kyc/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self) -> str:
        return f"KYCDocument({self.user.username}, {self.status})"
