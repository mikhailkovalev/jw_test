import os

from celery import (
    Celery,
)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jw_test.settings')

app = Celery(
    'jw_test',
)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {}'.format(repr(self.request)))
