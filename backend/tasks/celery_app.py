import os
import logging
from celery import Celery

# Setup logging
logger = logging.getLogger(__name__)

# Retrieve Redis URL from environment variables, defaulting to local redis
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Create the Celery application
celery_app = Celery(
    'ashtalakshmi_mrv',
    broker=redis_url,
    backend=redis_url,
    include=[
        'backend.tasks.ingest_scenes',
        'backend.tasks.compute_indices',
        'backend.tasks.biomass_inference',
        'backend.tasks.generate_report'
    ]
)

# Configure the Celery application
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Kolkata',
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_soft_time_limit=3600,  # 1 hour
    task_time_limit=7200,       # 2 hours
)

logger.info("Celery application 'ashtalakshmi_mrv' configured successfully.")
