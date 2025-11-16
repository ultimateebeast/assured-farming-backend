from rest_framework import serializers
from .models import Contract, PriceProposal, EscrowTransaction, Shipment, Dispute
from marketplace.serializers import ListingSerializer
from marketplace.models import Listing
from django.contrib.auth import get_user_model

User = get_user_model()


class PriceProposalSerializer(serializers.ModelSerializer):
    proposer = serializers.StringRelatedField(read_only=True)
    contract = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PriceProposal
        fields = ('id', 'contract', 'proposer', 'price_per_unit', 'message', 'created_at', 'accepted')
        read_only_fields = ('id', 'created_at', 'proposer', 'accepted', 'contract')


class ContractSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all(), source='listing', write_only=True)
    proposals = PriceProposalSerializer(many=True, read_only=True)

    class Meta:
        model = Contract
        fields = (
            'id', 'listing', 'listing_id', 'buyer', 'agreed_quantity', 'price_per_unit',
            'total_value', 'start_date', 'end_date', 'status', 'signed_at', 'proposals'
        )
        read_only_fields = ('id', 'buyer', 'status', 'signed_at', 'proposals')

    def create(self, validated_data):
        from decimal import Decimal, InvalidOperation

        user = self.context['request'].user
        listing = validated_data.get('listing')
        qty = validated_data.get('agreed_quantity')
        ppu = validated_data.get('price_per_unit')

        # Normalize to Decimal safely (handles if they are already Decimal)
        try:
            qty = Decimal(str(qty))
            ppu = Decimal(str(ppu))
        except (InvalidOperation, TypeError):
            raise serializers.ValidationError({
                'agreed_quantity': 'Invalid quantity',
                'price_per_unit': 'Invalid price per unit',
            })

        if qty <= 0:
            raise serializers.ValidationError({'agreed_quantity': 'Must be greater than 0'})
        if ppu <= 0:
            raise serializers.ValidationError({'price_per_unit': 'Must be greater than 0'})

        # Validate against listing availability if available
        available = getattr(listing, 'quantity_available', None)
        if available is None:
            available = getattr(listing, 'quantity', None)
        try:
            if available is not None and Decimal(str(available)) < qty:
                raise serializers.ValidationError({'agreed_quantity': 'Exceeds available quantity'})
        except (InvalidOperation, TypeError):
            pass

        validated_data['buyer'] = user
        validated_data['agreed_quantity'] = qty
        validated_data['price_per_unit'] = ppu
        # Compute total_value server-side to avoid float errors
        validated_data['total_value'] = qty * ppu
        # Default status when creating a new offer/contract
        if not validated_data.get('status'):
            validated_data['status'] = 'pending'

        return super().create(validated_data)


class EscrowTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscrowTransaction
        fields = ('id', 'contract', 'amount', 'status', 'payment_reference', 'created_at')
        read_only_fields = ('id', 'status', 'created_at')


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ('id', 'contract', 'pickup_date', 'delivery_date', 'tracking_id', 'delivered')


class DisputeSerializer(serializers.ModelSerializer):
    raised_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Dispute
        fields = ('id', 'contract', 'raised_by', 'description', 'status', 'resolution_notes', 'created_at')
        read_only_fields = ('id', 'raised_by', 'status', 'created_at')
