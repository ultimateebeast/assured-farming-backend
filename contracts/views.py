from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import Contract, PriceProposal, EscrowTransaction, Shipment, Dispute
from .serializers import ContractSerializer, PriceProposalSerializer, EscrowTransactionSerializer, ShipmentSerializer, DisputeSerializer
from payments.mock_gateway import create_mock_charge
from payments.tasks import send_email_task
# from payments.tasks import generate_contract_pdf_task


    
class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.select_related('listing', 'buyer').all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def propose_price(self, request, pk=None):
        contract = self.get_object()
        serializer = PriceProposalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        proposal = serializer.save(contract=contract, proposer=request.user)
        # notify counterparty
        send_email_task.delay('proposal_created', {'proposal_id': proposal.pk})
        return Response(PriceProposalSerializer(proposal).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def accept_proposal(self, request, pk=None):
        contract = self.get_object()
        proposal_id = request.data.get('proposal_id')
        try:
            proposal = contract.proposals.get(pk=proposal_id)
        except PriceProposal.DoesNotExist:
            return Response({'detail': 'Proposal not found'}, status=status.HTTP_404_NOT_FOUND)

        # mark accepted and update contract price
        with transaction.atomic():
            proposal.accepted = True
            proposal.save()
            contract.price_per_unit = proposal.price_per_unit
            contract.total_value = proposal.price_per_unit * contract.agreed_quantity
            contract.status = 'accepted'
            contract.save()
            # create escrow placeholder using mock gateway
            payment = create_mock_charge(contract=contract, amount=float(contract.total_value))
            EscrowTransaction.objects.create(contract=contract, amount=contract.total_value, status='held', payment_reference=payment['payment_reference'])
        send_email_task.delay('proposal_accepted', {'contract_id': contract.pk})
        return Response({'detail': 'Proposal accepted, escrow created'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        contract = self.get_object()
        # mark signed and generate signed PDF asynchronously
        contract.signed_at = timezone.now()
        contract.status = 'active'
        contract.save()
        # enqueue PDF generation task which will render and attach signed PDF
        generate_contract_pdf_task.delay(contract.pk)
        send_email_task.delay('contract_signed', {'contract_id': contract.pk})
        return Response({'detail': 'Contract signed; generating PDF'}, status=status.HTTP_200_OK)


class EscrowViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EscrowTransaction.objects.select_related('contract').all()
    serializer_class = EscrowTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.select_related('contract').all()
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def confirm_delivery(self, request, pk=None):
        shipment = self.get_object()
        shipment.delivered = True
        shipment.delivery_date = request.data.get('delivery_date') or shipment.delivery_date
        shipment.save()
        # release escrow (in production this would go through checks and admin review)
        escrow = shipment.contract.escrow
        escrow.status = 'released'
        escrow.save()
        send_email_task.delay('shipment_delivered', {'contract_id': shipment.contract.pk})
        return Response({'detail': 'Delivery confirmed and escrow released'})


class DisputeViewSet(viewsets.ModelViewSet):
    queryset = Dispute.objects.select_related('contract', 'raised_by').all()
    serializer_class = DisputeSerializer
    permission_classes = [permissions.IsAuthenticated]
