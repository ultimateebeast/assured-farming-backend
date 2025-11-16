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
        # Read crop_name from initial_data to be robust with multipart/form-data
        crop_name = self.initial_data.get('crop_name') or validated_data.pop('crop_name', None)
        if crop_name and not validated_data.get('crop'):
            crop_obj, _ = Crop.objects.get_or_create(name=str(crop_name).strip(), defaults={
                'variety': '',
                'unit': 'kg',
                'typical_price_range': ''
            })
            validated_data['crop'] = crop_obj

        validated_data['farmer'] = request.user
        return super().create(validated_data)

    def validate(self, data):
        # Ensure either crop or crop_name is provided
        crop_name = self.initial_data.get('crop_name')
        if not data.get('crop') and not crop_name:
            raise serializers.ValidationError({'crop': 'Provide either crop_id or crop_name.'})

        # Build a temporary instance for model.clean without unknown fields
        temp = {k: v for k, v in data.items() if k != 'crop_name'}
        instance = Listing(**{**temp, 'farmer': self.context['request'].user, 'crop': data.get('crop')})
        instance.clean()
        return data
