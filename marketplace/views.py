from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Crop, Listing
from .serializers import CropSerializer, ListingSerializer
from django_filters.rest_framework import DjangoFilterBackend


class CropViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    permission_classes = [permissions.AllowAny]


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.select_related('crop', 'farmer').all().order_by('-created_at')
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['crop', 'location', 'quality_grade']
    search_fields = ['crop__name', 'location']
    ordering_fields = ['price_floor', 'harvest_date']

    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        qs = self.get_queryset()[:10]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
