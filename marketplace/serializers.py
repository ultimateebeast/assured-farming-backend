from rest_framework import serializers
from .models import Crop, Listing


class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = ('id', 'name', 'variety', 'unit', 'typical_price_range')


class ListingSerializer(serializers.ModelSerializer):
    crop = CropSerializer(read_only=True)
    crop_id = serializers.PrimaryKeyRelatedField(queryset=Crop.objects.all(), source='crop', write_only=True)

    class Meta:
        model = Listing
        fields = ('id', 'farmer', 'crop', 'crop_id', 'quantity_available', 'harvest_date', 'quality_grade', 'location', 'price_floor', 'created_at')
        read_only_fields = ('id', 'farmer', 'created_at', 'crop')

    def create(self, validated_data):
        request = self.context['request']
        validated_data['farmer'] = request.user
        return super().create(validated_data)

    def validate(self, data):
        # reuse model clean rules
        instance = Listing(**{**data, 'farmer': self.context['request'].user})
        instance.clean()
        return data
