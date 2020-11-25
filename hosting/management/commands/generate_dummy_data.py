from itertools import (
    cycle,
)
from functools import (
    lru_cache,
)
from random import (
    choice,
    randint,
)

from lorem.text import (
    TextLorem,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
    Tuple,
    Type,
)

from django.conf import (
    settings,
)
from django.contrib.auth.models import (
    Permission,
    User,
)
from django.core.management import (
    BaseCommand,
)
from django.utils.crypto import (
    get_random_string,
)

from hosting.models import (
    AbstractContent,
    AbstractFile,
    AudioContent,
    AudioFile,
    Post,
    PostContent,
    SubtitleFile,
    TextContent,
    VideoContent,
    VideoFile,
)

if TYPE_CHECKING:
    from django.core.management import (
        CommandParser,
    )


class Command(BaseCommand):
    lorem = TextLorem(
        srange=(1, 3),
        trange=(1, 4),
    )

    def add_arguments(self, parser: 'CommandParser'):
        parser.add_argument(
            '-u',
            '--user',
            dest='username',
            help=(
                'Name of user published generated'
                'content. If there is no user with'
                'such name it would be created. If'
                'name is not provided script takes'
                'first found user.'
            ),
        )
        parser.add_argument(
            '-p',
            '--posts',
            dest='posts_count',
            type=int,
            default=10,
            help=(
                'Posts count to generate.'
            ),
        )
        parser.add_argument(
            '--max-attachments',
            dest='max_attachments',
            type=int,
            default=10,
            help=(
                'Max number of attachments in post.'
            ),
        )
        parser.add_argument(
            '--min-attachments',
            dest='min_attachments',
            type=int,
            default=2,
            help=(
                'Min number of attachments in post.'
            ),
        )

    def handle(
            self,
            username: Optional[str],
            posts_count: int,
            max_attachments: int,
            min_attachments: int,
            *args,
            **options,
    ):
        user = self._get_user(
            username=username,
        )
        self._create_posts(
            posts_count=posts_count,
            publisher=user,
            max_attachments=max_attachments,
            min_attachments=min_attachments,
        )

    @classmethod
    def _get_user(cls, username: Optional[str]) -> User:
        if username is not None:
            user = User.objects.filter(
                username=username,
            ).first()

            if user is None:
                user = User(
                    username=username,
                    is_staff=True,
                )
                user.set_password(username)
                user.save()
        else:
            user = User.objects.first()
            if user is None:
                raise ValueError(
                    'There is no users in DB! Use'
                    '`--username` to create one or'
                    'create it manually.'
                )

        assert isinstance(user, User)
        cls._assign_permissions(
            user=user,
        )
        return user

    @staticmethod
    def _assign_permissions(user: User):
        permissions = Permission.objects.filter(
            content_type__app_label='hosting',
        ).values_list(
            'pk',
            flat=True,
        )

        for permission in permissions:
            user.user_permissions.add(
                permission,
            )

    def _create_posts(
            self,
            posts_count: int,
            publisher: User,
            max_attachments: int,
            min_attachments: int,
    ) -> Tuple[Post, ...]:
        created_posts = tuple(
            Post.objects.create(
                publisher=publisher,
            )
            for _ in range(posts_count)
        )

        for post in created_posts:
            attachments_count = randint(
                min_attachments,
                max_attachments,
            )
            for position, fabric_name in zip(range(1, 1+attachments_count), self.fabric_names):
                PostContent.objects.create(
                    post=post,
                    attachment=self._make_attachment(fabric_name),
                    position=position,
                )

        return created_posts

    @classmethod
    def _make_attachment(cls, fabric_name):
        return getattr(cls, fabric_name)(
            **cls._make_abstract_content_params(),
        )

    @classmethod
    def _make_abstract_content_params(cls) -> Dict[str, Any]:
        return dict(
            title=cls.lorem.sentence(),
        )

    VIDEO_FILE_EXTENSIONS = (
        'mp4',
        'mkv',
        'avi',
    )
    SUBTITLE_FILE_EXTENSIONS = (
        'vvt',
        'srt',
    )
    AUDIO_FILE_EXTENSIONS = (
        'mp3',
        'm4a',
        'ogg',
    )

    @classmethod
    def _create_file(
            cls,
            filename: str,
            fabric: Type[AbstractFile],
            content: 'AbstractContent',
            **extra,
    ):
        mock_file = open(settings.MEDIA_ROOT/filename, mode='w')
        with mock_file:
            pass
        # create empty mock file

        fabric.objects.create(
            file=filename,
            content=content,
            **extra,
        )

    @classmethod
    def _make_video_content(cls, **abstract_content_params):
        content = VideoContent.objects.create(
            **abstract_content_params,
        )
        cls._create_file(
            '{filename}.{ext}'.format(
                filename=get_random_string(),
                ext=choice(cls.VIDEO_FILE_EXTENSIONS),
            ),
            content=content,
            fabric=VideoFile,
        )
        if choice((True, False)):
            cls._create_file(
                '{filename}.{ext}'.format(
                    filename=get_random_string(),
                    ext=choice(cls.SUBTITLE_FILE_EXTENSIONS),
                ),
                content=content,
                fabric=SubtitleFile,
            )

        return content

    @classmethod
    def _make_audio_content(cls, **abstract_content_params):
        content = AudioContent.objects.create(
            **abstract_content_params,
        )
        cls._create_file(
            '{filename}.{ext}'.format(
                filename=get_random_string(),
                ext=choice(cls.AUDIO_FILE_EXTENSIONS),
            ),
            content=content,
            fabric=AudioFile,
            bitrate=choice((320, 192, 128)),
        )

        return content

    @classmethod
    def _make_text_content(cls, **abstract_content_params):
        content = TextContent.objects.create(
            content=cls.lorem.text(),
            **abstract_content_params,
        )
        return content

    _specific_content_fabrics = (
        '_make_video_content',
        '_make_audio_content',
        '_make_text_content',
    )

    @property
    @lru_cache(maxsize=None)
    def fabric_names(self):
        return cycle(self._specific_content_fabrics)

