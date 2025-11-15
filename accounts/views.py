from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegisterSerializer, UserSerializer, KYCDocumentSerializer
from .models import KYCDocument, FarmerProfile, BuyerProfile
from rest_framework.parsers import MultiPartParser, FormParser
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


# ✅ 1. /api/v1/accounts/register/
class RegisterTokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info(f"Registration attempt with data: {request.data}")
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User {user.username} registered successfully")

            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)

            return Response(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "access": access,
                    "refresh": str(refresh),
                },
                status=status.HTTP_201_CREATED,
            )
        logger.error(f"Registration failed with errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ 2. /api/v1/accounts/me/
class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ✅ 3. /api/v1/accounts/kyc/upload/
class KYCUploadView(APIView):
    """Upload KYC documents for verification."""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        user = request.user
        
        # Check if user is farmer or buyer
        if user.role not in ['farmer', 'buyer']:
            return Response(
                {"error": "Only farmers and buyers can upload KYC documents."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check file size (max 5MB)
        document = request.FILES.get('document')
        if not document:
            return Response(
                {"error": "No document provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if document.size > 5 * 1024 * 1024:  # 5MB
            return Response(
                {"error": "File size exceeds 5MB limit."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create KYC document record
        kyc_doc = KYCDocument.objects.create(
            user=user,
            document=document,
            doc_type=request.data.get('doc_type', 'ID'),
        )

        serializer = KYCDocumentSerializer(kyc_doc)
        return Response(serializer.data, status=status.HTTP_201_CREATED)