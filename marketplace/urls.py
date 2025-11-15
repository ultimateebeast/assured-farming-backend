from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CropViewSet, ListingViewSet

router = DefaultRouter()
router.register('crops', CropViewSet, basename='crop')
router.register('listings', ListingViewSet, basename='listing')

urlpatterns = [
    path('', include(router.urls)),
]
