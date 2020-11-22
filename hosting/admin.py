from functools import (
    lru_cache,
)

from django.contrib import (
    admin,
)
from polymorphic.admin import (
    PolymorphicChildModelAdmin,
    PolymorphicParentModelAdmin,
)

from .models import (
    AbstractContent,
    AudioContent,
    AudioFile,
    Post,
    PostContent,
    SubtitleFile,
    TextContent,
    VideoContent,
    VideoFile,
)


class PostContentAdmin(admin.StackedInline):
    model = PostContent
    fields = (
        'attachment',
        'position',
        'views_count',
    )
    readonly_fields = (
        'views_count',
    )
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fields = (
        'publisher',
    )
    inlines = (
        PostContentAdmin,
    )


class AbstractContentChildAdmin(PolymorphicChildModelAdmin):
    base_model = AbstractContent
    fields = (
        'title',
    )


@admin.register(TextContent)
class TextContentAdmin(AbstractContentChildAdmin):
    base_model = TextContent

    @property
    @lru_cache(maxsize=None)
    def fields(self):
        return super().fields + (
            'content',
        )


class AbstractFileInline(admin.StackedInline):
    fields = (
        'file',
    )
    extra = 1


class VideoFileInline(AbstractFileInline):
    model = VideoFile


class AudioFileInline(AbstractFileInline):
    model = AudioFile

    @property
    @lru_cache(maxsize=None)
    def fields(self):
        return super().fields + (
            'bitrate',
        )


class SubtitleFileInline(AbstractFileInline):
    model = SubtitleFile


@admin.register(VideoContent)
class VideoContentAdmin(AbstractContentChildAdmin):
    base_model = VideoContent
    inlines = (
        VideoFileInline,
        SubtitleFileInline,
    )


@admin.register(AudioContent)
class AudioContentAdmin(AbstractContentChildAdmin):
    base_model = AudioContent
    inlines = (
        AudioFileInline,
    )


@admin.register(AbstractContent)
class AbstractContentAdmin(PolymorphicParentModelAdmin):
    base_model = AbstractContent
    child_models = (
        AudioContent,
        TextContent,
        VideoContent,
    )
