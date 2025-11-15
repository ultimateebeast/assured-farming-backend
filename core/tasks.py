# core/tasks.py
from celery import shared_task
import time
import logging

logger = logging.getLogger(__name__)

@shared_task
def test_celery_task():
    logger.info("✅ Celery test task started...")
    time.sleep(2)
    logger.info("✅ Celery test task completed!")
    return "Celery is working!"
