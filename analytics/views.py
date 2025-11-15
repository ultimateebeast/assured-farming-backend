"""Analytics API endpoints for farmer and market metrics."""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from contracts.models import Contract, EscrowTransaction, Shipment


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def farmer_revenue(request):
    """GET /api/v1/analytics/farmer-revenue/ - farmer revenue from completed contracts."""
    if request.user.role != 'farmer':
        return Response({'detail': 'Only farmers can view revenue'}, status=status.HTTP_403_FORBIDDEN)
    
    total = EscrowTransaction.objects.filter(
        contract__listing__farmer=request.user,
        status='released'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    return Response({'farmer_id': request.user.id, 'total_revenue': total})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def active_contracts(request):
    """GET /api/v1/analytics/active-contracts/ - count of active contracts for user."""
    user = request.user
    count = Contract.objects.filter(
        Q(buyer=user) | Q(listing__farmer=user),
        status__in=['accepted', 'active']
    ).count()
    
    return Response({'user_id': user.id, 'active_contracts': count})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def avg_delivery_time(request):
    """GET /api/v1/analytics/avg-delivery-time/ - average days to delivery."""
    user = request.user
    shipments = Shipment.objects.filter(
        contract__listing__farmer=user,
        delivered=True
    ).annotate(
        days_to_delivery=models.F('delivery_date') - models.F('contract__start_date')
    )
    
    avg_days = shipments.aggregate(Avg('days_to_delivery'))['days_to_delivery__avg']
    
    return Response({'avg_days_to_delivery': avg_days})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def proposals_acceptance_rate(request):
    """GET /api/v1/analytics/acceptance-rate/ - ratio of accepted proposals."""
    user = request.user
    total = request.query_params.get('user', user.id)
    
    from contracts.models import PriceProposal
    accepted = PriceProposal.objects.filter(proposer=user, accepted=True).count()
    total_proposals = PriceProposal.objects.filter(proposer=user).count()
    
    rate = (accepted / total_proposals * 100) if total_proposals > 0 else 0
    
    return Response({
        'user_id': user.id,
        'accepted_proposals': accepted,
        'total_proposals': total_proposals,
        'acceptance_rate': f'{rate:.2f}%'
    })
