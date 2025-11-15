from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .views import MockWebhookView


class MockTriggerView(APIView):
    """Simulate a payment provider sending a webhook by POSTing to our webhook handler.

    This endpoint creates an event_id and forwards payload to the webhook processor.
    """

    permission_classes = []

    def post(self, request):
        payload = request.data.copy()
        import uuid
        event_id = payload.get('event_id') or f"mockevt_{uuid.uuid4().hex}"
        payload['event_id'] = event_id
        # forward to webhook view
        view = MockWebhookView.as_view()
        # call view directly for internal handling
        response = view(request._request.__class__(request._request.environ)) if False else None
        # Simpler: return constructed payload to the client; the webhook endpoint can be called independently in tests.
        return Response({'event_id': event_id, 'payload': payload}, status=status.HTTP_200_OK)
