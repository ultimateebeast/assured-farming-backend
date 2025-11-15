from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from marketplace.models import Crop, Listing
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed demo data: users, crops, listings'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username='farmer1').exists():
            farmer = User.objects.create_user('farmer1', email='farmer1@example.com', password='pass1234', role='farmer')
            print('Created farmer1')
        if not User.objects.filter(username='buyer1').exists():
            buyer = User.objects.create_user('buyer1', email='buyer1@example.com', password='pass1234', role='buyer')
            print('Created buyer1')

        # crops
        rice, _ = Crop.objects.get_or_create(name='Rice', variety='Basmati', unit='kg')
        wheat, _ = Crop.objects.get_or_create(name='Wheat', variety='Durum', unit='kg')

        # listings
        farmer = User.objects.filter(role='farmer').first()
        if farmer:
            Listing.objects.get_or_create(farmer=farmer, crop=rice, quantity_available=1000, harvest_date=timezone.now().date(), price_floor=30)
            Listing.objects.get_or_create(farmer=farmer, crop=wheat, quantity_available=500, harvest_date=timezone.now().date(), price_floor=28)
            print('Created sample listings')

        print('Seed data finished')
