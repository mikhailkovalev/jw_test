from django.conf import (
    settings,
)
from django.contrib.auth.models import (
    User,
)
from django.urls import (
    reverse,
)
from rest_framework.test import (
    APIRequestFactory,
    APITestCase,
    force_authenticate,
)

from .models import (
    Post,
)
from .views import (
    PostViewSet,
)


class PostTests(APITestCase):

    def test_post_page_size(self):
        """
        Ensure page contains settings.REST_PAGE_SIZE items
        """
        url = reverse('post-list')
        user = User.objects.first()
        self.assertIsNotNone(user)

        factory = APIRequestFactory()
        request = factory.get(url)
        force_authenticate(request, user)

        list_view = PostViewSet.as_view({'get': 'list'})
        response = list_view(request)

        total_posts = Post.objects.count()

        self.assertEqual(
            len(response.data['results']),
            min(settings.REST_PAGE_SIZE, total_posts),
        )
