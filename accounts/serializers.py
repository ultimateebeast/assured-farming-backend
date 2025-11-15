from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import KYCDocument, FarmerProfile, BuyerProfile

User = get_user_model()


class FarmerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerProfile
        fields = ['id', 'kyc_status', 'farm_locations', 'bank_details_masked']
        read_only_fields = ['id', 'kyc_status']


class BuyerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerProfile
        fields = ['id', 'company_name', 'gst_number', 'contact_person', 'kyc_status']
        read_only_fields = ['id', 'kyc_status']


class UserSerializer(serializers.ModelSerializer):
    farmer_profile = FarmerProfileSerializer(read_only=True)
    buyer_profile = BuyerProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'role', 'is_verified',
            'farmer_profile', 'buyer_profile'
        ]
        read_only_fields = ['id', 'is_verified']


class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = ['id', 'user', 'doc_type', 'document', 'status', 'uploaded_at']
        read_only_fields = ['id', 'user', 'uploaded_at', 'status']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=['farmer', 'buyer'])
    phone = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'phone', 'role']

    def validate(self, data):
        """Validate passwords match."""
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """Create user and associated profile."""
        role = validated_data.pop('role')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data['phone'],
            role=role,
        )

        # Create appropriate profile based on role
        if role == 'farmer':
            FarmerProfile.objects.create(user=user, kyc_status='pending')
        elif role == 'buyer':
            BuyerProfile.objects.create(user=user, kyc_status='pending')

        return user