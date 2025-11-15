from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Crop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('variety', models.CharField(blank=True, max_length=128)),
                ('unit', models.CharField(default='kg', max_length=32)),
                ('typical_price_range', models.CharField(blank=True, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_available', models.DecimalField(decimal_places=3, max_digits=12)),
                ('harvest_date', models.DateField()),
                ('quality_grade', models.CharField(blank=True, max_length=32)),
                ('location', models.CharField(blank=True, max_length=255)),
                ('price_floor', models.DecimalField(max_digits=12, decimal_places=2)),
                ('created_at', models.DateTimeField()),
                ('crop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings', to='marketplace.crop')),
            ],
        ),
    ]
