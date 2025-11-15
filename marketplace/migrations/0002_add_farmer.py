from django.db import migrations, models
import django.db.models.deletion
import django.conf


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='farmer',
            field=models.ForeignKey(
                to=django.conf.settings.AUTH_USER_MODEL,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='listings',
                null=True,
                blank=True,
            ),
        ),
    ]
