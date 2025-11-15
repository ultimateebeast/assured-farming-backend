from django.contrib import admin
from .models import Contract, PriceProposal, EscrowTransaction, Shipment, Dispute


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'buyer', 'status', 'created_at')
    readonly_fields = ('created_at', 'signed_at')


@admin.register(PriceProposal)
class PriceProposalAdmin(admin.ModelAdmin):
    list_display = ('id', 'contract', 'proposer', 'price_per_unit', 'accepted', 'created_at')


@admin.register(EscrowTransaction)
class EscrowAdmin(admin.ModelAdmin):
    list_display = ('id', 'contract', 'amount', 'status', 'payment_reference')


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'contract', 'tracking_id', 'delivered')


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ('id', 'contract', 'raised_by', 'status', 'created_at')
