from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ContractViewSet, EscrowViewSet, ShipmentViewSet, DisputeViewSet

router = DefaultRouter()
router.register('contracts', ContractViewSet, basename='contract')
router.register('escrows', EscrowViewSet, basename='escrow')
router.register('shipments', ShipmentViewSet, basename='shipment')
router.register('disputes', DisputeViewSet, basename='dispute')

urlpatterns = [
    path('', include(router.urls)),
]
