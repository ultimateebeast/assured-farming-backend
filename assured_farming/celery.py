# assured_farming/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assured_farming.settings')

app = Celery('assured_farming')

# Read config from Django settings, using CELERY_ prefix in settings if desired
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks in all installed apps' tasks.py modules
app.autodiscover_tasks()
