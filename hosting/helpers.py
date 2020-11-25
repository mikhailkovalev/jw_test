from contextlib import (
    contextmanager,
)

from django.core.cache import (
    cache,
)


LOCK_EXPIRE = 5


@contextmanager
def memcache_lock(lock_id, oid):
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        if status:
            cache.delete(lock_id)
