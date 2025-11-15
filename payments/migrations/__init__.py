"""Migration for WebhookEvent model for payments app."""
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WebhookEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.CharField(max_length=255, unique=True)),
                ('payload', models.JSONField(default=dict)),
                ('received_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
