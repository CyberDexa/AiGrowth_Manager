"""
Celery Application Configuration

Configures Celery for background task processing with Redis as broker and result backend.
Used for scheduled post publishing and other async operations.
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    'ai_growth_manager',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.tasks.publishing_tasks']  # Auto-discover tasks
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        'master_name': 'mymaster',
        'visibility_timeout': 3600,
    },
    
    # Task execution settings
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,  # Reject task if worker dies
    task_time_limit=300,  # 5 minutes hard limit
    task_soft_time_limit=240,  # 4 minutes soft limit
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Fetch one task at a time (for long-running tasks)
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (prevent memory leaks)
    
    # Beat schedule (for periodic tasks)
    beat_schedule={
        'check-scheduled-posts-every-minute': {
            'task': 'app.tasks.publishing_tasks.check_and_publish_scheduled_posts',
            'schedule': crontab(minute='*/1'),  # Every minute
            'options': {'expires': 55}  # Expire if not executed within 55 seconds
        },
        'cleanup-old-scheduled-posts': {
            'task': 'app.tasks.publishing_tasks.cleanup_old_scheduled_posts',
            'schedule': crontab(hour='*/6'),  # Every 6 hours
            'options': {'expires': 3500}  # Expire if not executed within ~1 hour
        }
    },
    
    # Retry settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # Logging
    worker_hijack_root_logger=False,  # Don't override root logger
)

# Task routes (for queue management)
celery_app.conf.task_routes = {
    'app.tasks.publishing_tasks.*': {'queue': 'publishing'},
    'app.tasks.analytics_tasks.*': {'queue': 'analytics'},
}

logger.info("✅ Celery app configured successfully")

# For Celery worker to discover tasks
if __name__ == '__main__':
    celery_app.start()
