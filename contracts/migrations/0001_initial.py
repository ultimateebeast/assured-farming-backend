from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('marketplace', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agreed_quantity', models.DecimalField(decimal_places=3, max_digits=12)),
                ('price_per_unit', models.DecimalField(max_digits=12, decimal_places=2)),
                ('total_value', models.DecimalField(max_digits=14, decimal_places=2)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(default='draft', max_length=32)),
                ('contract_document', models.FileField(blank=True, null=True, upload_to='contracts/')),
                ('signed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_contracts', to='accounts.user')),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='marketplace.listing')),
            ],
        ),
        migrations.CreateModel(
            name='PriceProposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_per_unit', models.DecimalField(max_digits=12, decimal_places=2)),
                ('message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('accepted', models.BooleanField(default=False)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proposals', to='contracts.contract')),
                ('proposer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.user')),
            ],
        ),
        migrations.CreateModel(
            name='EscrowTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(max_digits=14, decimal_places=2)),
                ('status', models.CharField(default='pending', max_length=16)),
                ('payment_reference', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('contract', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='escrow', to='contracts.contract')),
            ],
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_date', models.DateField(blank=True, null=True)),
                ('delivery_date', models.DateField(blank=True, null=True)),
                ('tracking_id', models.CharField(blank=True, max_length=255)),
                ('delivered', models.BooleanField(default=False)),
                ('contract', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='shipment', to='contracts.contract')),
            ],
        ),
        migrations.CreateModel(
            name='Dispute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('status', models.CharField(default='open', max_length=32)),
                ('resolution_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disputes', to='contracts.contract')),
                ('raised_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.user')),
            ],
        ),
    ]
