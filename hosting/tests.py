from operator import (
    attrgetter,
)
from time import (
    sleep,
)

from celery.states import (
    READY_STATES,
)
from django.conf import (
    settings,
)
from django.contrib.auth.models import (
    User,
)
from django.core.management import (
    call_command,
)
from django.test import (
    tag,
)
from django.test.testcases import (
    SimpleTestCase,
)
from django.urls import (
    reverse,
)
from rest_framework.test import (
    APIRequestFactory,
    APITestCase,
    force_authenticate,
)

from .helpers import (
    LOCK_EXPIRE,
)
from .management.commands.generate_dummy_data import (
    Command as GenerateDummyDataCommand,
)
from .models import (
    AbstractContent,
    AudioContent,
    Post,
    PostContent,
    TextContent,
    VideoContent,
)
from .tasks import (
    increment_views_count,
)
from .views import (
    PostViewSet,
)


class _BaseTests(APITestCase):
    test_user = 'test'

    def _get_authenticated_request(self, url):
        user = User.objects.filter(
            username=self.test_user,
        ).first()
        self.assertIsNotNone(user)

        factory = APIRequestFactory()
        request = factory.get(url)
        force_authenticate(request, user)

        return request


class _PostsListTest:
    def test_post_page_size(self):
        """
        Ensure page contains settings.REST_PAGE_SIZE items
        """
        url = reverse('post-list')

        request = self._get_authenticated_request(url)

        list_view = PostViewSet.as_view({'get': 'list'})
        response = list_view(request)

        total_posts = Post.objects.count()

        self.assertEqual(
            len(response.data['results']),
            min(settings.REST_PAGE_SIZE, total_posts),
        )


class PostsFullPageTest(_PostsListTest, _BaseTests):
    """
    When count of posts is more than
    settings.REST_PAGE_SIZE, we should get exactly
    settings.REST_PAGE_SIZE items on the first page.
    """
    def setUp(self):
        command = GenerateDummyDataCommand()
        call_command(
            command,
            user=self.test_user,
            posts=settings.REST_PAGE_SIZE+1,
            max_attachments=1,
            min_attachments=1,
        )


class PostsSmallPageTest(_PostsListTest, _BaseTests):
    """
    When count of posts is less than
    settings.REST_PAGE_SIZE, we should get all posts
    on the first page
    """

    def setUp(self):
        command = GenerateDummyDataCommand()
        call_command(
            command,
            user=self.test_user,
            posts=settings.REST_PAGE_SIZE-1,
            max_attachments=1,
            min_attachments=1,
        )


class PostDetailsTest(_BaseTests):
    def setUp(self):
        command = GenerateDummyDataCommand()
        call_command(
            command,
            user=self.test_user,
            posts=1,
            max_attachments=3,
            min_attachments=3,
        )

    def _test_specific_params(self, model, attr_sets):
        self.assertTrue(issubclass(model, AbstractContent))

        content = model.objects.first()
        self.assertIsNotNone(content)

        post = content.posts.first()
        self.assertIsNotNone(content)

        through = PostContent.objects.filter(
            post_id=post.pk,
            attachment_id=content.pk,
        ).first()
        self.assertIsNotNone(through)

        kw = {'pk': post.pk}
        url = reverse('post-detail', kwargs=kw)
        request = self._get_authenticated_request(url)

        detail_view = PostViewSet.as_view({'get': 'retrieve'})
        response = detail_view(request, **kw)
        self.assertIn('attachments', response.data)

        response_item = next(
            (
                item
                for item in response.data['attachments']
                if item['position'] == through.position
            ),
            None,
        )
        self.assertIsNotNone(response_item)

        for attr_set in attr_sets:
            nested_obj = response_item
            for attr in attr_set:
                if isinstance(nested_obj, (list, tuple)):
                    nested_obj = nested_obj[0]
                self.assertIn(attr, nested_obj)
                nested_obj = nested_obj[attr]

    def test_text_params(self):
        self._test_specific_params(
            model=TextContent,
            attr_sets=(
                ('content',),
            ),
        )

    def test_audio_params(self):
        self._test_specific_params(
            model=AudioContent,
            attr_sets=(
                ('files', 'bitrate'),
            ),
        )

    def test_video_params(self):
        self._test_specific_params(
            model=VideoContent,
            attr_sets=(
                ('files',),
                ('subtitles',),
            ),
        )


class CeleryTests(SimpleTestCase):
    databases = (
        'default',
    )
    test_user = 'test'

    def setUp(self):
        if not Post.objects.exists():
            command = GenerateDummyDataCommand()
            call_command(
                command,
                user=self.test_user,
                posts=1,
            )

    @tag('celery')
    def test_views_count_increment(self):
        post = Post.objects.first()
        self.assertIsNotNone(post)

        before_requests = dict(PostContent.objects.filter(
            post_id=post.pk,
        ).values_list(
            'pk',
            'views_count',
        ))

        requests_count = 10

        results = tuple(
            increment_views_count.delay(post.pk)
            for _ in range(requests_count)
        )

        while True:
            sleep(LOCK_EXPIRE)
            states = set(map(attrgetter('status'), results))
            if states.issubset(READY_STATES):
                break

        after_requests = dict(PostContent.objects.filter(
            post_id=post.pk,
        ).values_list(
            'pk',
            'views_count',
        ))

        for pk, before in before_requests.items():
            self.assertEqual(
                before + requests_count,
                after_requests[pk],
            )
