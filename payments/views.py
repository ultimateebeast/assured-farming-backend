from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from .models import WebhookEvent
from contracts.models import EscrowTransaction, Contract


class MockWebhookView(APIView):
    """Accepts webhook callbacks from the mock gateway.

    Payload expected: {"event_id": "<id>", "payment_reference": "<ref>", "status": "held|released|refunded"}
    This view is idempotent — we store processed event_id in WebhookEvent and ignore duplicates.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        event_id = data.get('event_id')
        payment_reference = data.get('payment_reference')
        new_status = data.get('status')

        if not event_id or not payment_reference or not new_status:
            return Response({'detail': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

        # idempotency: if we've seen this event_id, return 200
        if WebhookEvent.objects.filter(event_id=event_id).exists():
            return Response({'detail': 'Already processed'}, status=status.HTTP_200_OK)

        # process event
        with transaction.atomic():
            WebhookEvent.objects.create(event_id=event_id, payload=data)
            try:
                escrow = EscrowTransaction.objects.select_for_update().get(payment_reference=payment_reference)
            except EscrowTransaction.DoesNotExist:
                return Response({'detail': 'Escrow not found'}, status=status.HTTP_404_NOT_FOUND)

            if new_status not in dict(EscrowTransaction.STATUS_CHOICES):
                return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

            escrow.status = new_status
            escrow.save()

        return Response({'detail': 'processed'})
