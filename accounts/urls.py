from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterTokenView

urlpatterns = [
    path("register/", views.RegisterTokenView.as_view(), name="register"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.MeView.as_view(), name='api-me'),
    path('kyc/upload/', views.KYCUploadView.as_view(), name='api-kyc-upload'),
]
