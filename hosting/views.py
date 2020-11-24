from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.viewsets import (
    ModelViewSet,
)

from .models import (
    Post,
)
from .serializers import (
    PostDetailedSerializer,
    PostSerializer,
)
from .tasks import (
    increment_views_count,
)


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        IsAuthenticated,
    )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailedSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        result = super().retrieve(request, *args, **kwargs)
        increment_views_count.delay(
            post_id=kwargs['pk'],
        )
        return result



