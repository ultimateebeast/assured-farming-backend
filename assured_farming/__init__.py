import logging

logger = logging.getLogger(__name__)

try:
    from .celery import app as celery_app  # noqa
except ImportError:
    celery_app = None
except Exception as exc:
    # If something else fails (syntax, runtime in celery.py), surface it to logs
    logger.exception("Unexpected error importing Celery app: %s", exc)
    celery_app = None

__all__ = ("celery_app",)
