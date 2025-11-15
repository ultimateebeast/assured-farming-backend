from django.urls import path
from .views import MockWebhookView
from .views_trigger import MockTriggerView

urlpatterns = [
    path('mock/webhook/', MockWebhookView.as_view(), name='payments-mock-webhook'),
    path('mock/trigger/', MockTriggerView.as_view(), name='payments-mock-trigger'),
]
