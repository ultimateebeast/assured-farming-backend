from django.db import migrations


def seed_crops(apps, schema_editor):
    Crop = apps.get_model('marketplace', 'Crop')
    crops = [
        {"name": "Wheat", "variety": "Common", "unit": "kg"},
        {"name": "Rice", "variety": "Basmati", "unit": "kg"},
        {"name": "Maize", "variety": "Yellow Dent", "unit": "kg"},
        {"name": "Barley", "variety": "Two-row", "unit": "kg"},
        {"name": "Soybean", "variety": "Glycine max", "unit": "kg"},
        {"name": "Cotton", "variety": "Gossypium", "unit": "kg"},
        {"name": "Sugarcane", "variety": "Co 86032", "unit": "kg"},
        {"name": "Potato", "variety": "Russet", "unit": "kg"},
        {"name": "Tomato", "variety": "Heirloom", "unit": "kg"},
        {"name": "Onion", "variety": "Red", "unit": "kg"},
        {"name": "Chickpea", "variety": "Desi", "unit": "kg"},
        {"name": "Lentil", "variety": "Masoor", "unit": "kg"},
    ]

    for c in crops:
        Crop.objects.get_or_create(name=c["name"], defaults={
            "variety": c.get("variety", ""),
            "unit": c.get("unit", "kg"),
            "typical_price_range": ""
        })


def unseed_crops(apps, schema_editor):
    Crop = apps.get_model('marketplace', 'Crop')
    names = [
        "Wheat", "Rice", "Maize", "Barley", "Soybean", "Cotton",
        "Sugarcane", "Potato", "Tomato", "Onion", "Chickpea", "Lentil"
    ]
    Crop.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_auto_0004'),
    ]

    operations = [
        migrations.RunPython(seed_crops, unseed_crops),
    ]
