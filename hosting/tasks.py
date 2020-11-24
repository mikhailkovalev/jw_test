from celery import (
    shared_task,
)
from django.db.models import (
    F,
)

from .models import (
    PostContent,
)


@shared_task
def increment_views_count(post_id):
    PostContent.objects.filter(
        post_id=post_id,
    ).update(
        views_count=F('views_count')+1,
    )
