from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class Contract(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('proposed', 'Proposed'),
        ('accepted', 'Accepted'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('disputed', 'Disputed'),
        ('cancelled', 'Cancelled'),
    ]

    listing = models.ForeignKey('marketplace.Listing', on_delete=models.CASCADE, related_name='contracts')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_contracts')
    agreed_quantity = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal('0.001'))])
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    total_value = models.DecimalField(max_digits=14, decimal_places=2)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='draft')
    contract_document = models.FileField(upload_to='contracts/', null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Contract({self.pk}) {self.listing} - {self.buyer.username} [{self.status}]"


class PriceProposal(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='proposals')
    proposer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Proposal({self.pk}) for Contract {self.contract_id} by {self.proposer.username}"


class EscrowTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('held', 'Held'),
        ('released', 'Released'),
        ('refunded', 'Refunded'),
    ]

    contract = models.OneToOneField(Contract, on_delete=models.CASCADE, related_name='escrow')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending')
    payment_reference = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Escrow({self.pk}) {self.amount} [{self.status}]"


class Shipment(models.Model):
    contract = models.OneToOneField(Contract, on_delete=models.CASCADE, related_name='shipment')
    pickup_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    tracking_id = models.CharField(max_length=255, blank=True)
    delivered = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Shipment({self.pk}) for Contract {self.contract_id}"


class Dispute(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='disputes')
    raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='open')
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Dispute({self.pk}) on Contract {self.contract_id} by {self.raised_by.username}"
