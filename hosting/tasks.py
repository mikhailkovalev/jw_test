from time import (
    sleep,
)
from celery import (
    shared_task,
)
from django.db.models import (
    F,
)

from .helpers import (
    LOCK_EXPIRE,
    memcache_lock,
)
from .models import (
    PostContent,
)


@shared_task(bind=True)
def increment_views_count(self, post_id):
    lock_id = '{name}-lock-post-{post_id}'.format(
        name=self.name,
        post_id=post_id,
    )
    while True:
        with memcache_lock(lock_id, self.app.oid) as acquired:
            if acquired:
                result = PostContent.objects.filter(
                    post_id=post_id,
                ).update(
                    views_count=F('views_count') + 1,
                )
                return result
        if not acquired:
            sleep(LOCK_EXPIRE)
