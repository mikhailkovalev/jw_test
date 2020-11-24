import os

from celery import (
    Celery,
)
from django.conf import (
    settings,
)


os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'jw_test.settings',
)

app = Celery(
    'jw_test',
)

app.config_from_object(
    'django.conf:settings',
    namespace=settings.CELERY_NAMESPACE,
)

app.autodiscover_tasks()
