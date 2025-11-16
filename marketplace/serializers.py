from rest_framework import serializers
from .models import Crop, Listing


class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = ('id', 'name', 'variety', 'unit', 'typical_price_range')


class ListingSerializer(serializers.ModelSerializer):
    crop = CropSerializer(read_only=True)
    crop_id = serializers.PrimaryKeyRelatedField(queryset=Crop.objects.all(), source='crop', write_only=True, required=False)
    # Allow submitting crop_name when crop_id is not available (fallback)
    crop_name = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = Listing
        fields = (
            'id', 'farmer', 'crop', 'crop_id', 'crop_name',
            'quantity_available', 'harvest_date', 'quality_grade', 'location', 'price_floor', 'created_at'
        )
        read_only_fields = ('id', 'farmer', 'created_at', 'crop')

    def create(self, validated_data):
        request = self.context['request']
        # Extract crop_name if provided (do before super().create)
        crop_name = validated_data.pop('crop_name', None)
        # If crop not set via crop_id and crop_name provided, get_or_create it
        if not validated_data.get('crop') and crop_name:
            crop_obj, _ = Crop.objects.get_or_create(name=crop_name.strip(), defaults={
                'variety': '',
                'unit': 'kg',
                'typical_price_range': ''
            })
            validated_data['crop'] = crop_obj

        validated_data['farmer'] = request.user
        return super().create(validated_data)

    def validate(self, data):
        # Ensure either crop or crop_name is provided
        if not data.get('crop') and not self.initial_data.get('crop_name'):
            raise serializers.ValidationError({'crop': 'Provide either crop_id or crop_name.'})

        # reuse model clean rules
        instance = Listing(**{**data, 'farmer': self.context['request'].user})
        instance.clean()
        return data
