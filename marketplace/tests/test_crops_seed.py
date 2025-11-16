import pytest
from django.apps import apps

@pytest.mark.django_db
def test_seeded_crops_exist():
    Crop = apps.get_model('marketplace', 'Crop')
    names = {"Wheat", "Rice", "Maize", "Barley", "Soybean", "Cotton", "Sugarcane", "Potato", "Tomato", "Onion", "Chickpea", "Lentil"}
    existing = set(Crop.objects.values_list('name', flat=True))
    # At least 10 crops, and the common ones are present
    assert len(existing) >= 10
    assert {"Wheat", "Rice", "Maize"}.issubset(existing)
