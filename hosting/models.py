from django.db import models

from polymorphic.models import (
    PolymorphicModel,
)


class Post(models.Model):
    publisher = models.ForeignKey(
        verbose_name='Publisher',
        to='auth.User',
        on_delete=models.CASCADE,
        related_name='posts',
    )


class AbstractContent(PolymorphicModel):
    title = models.CharField(
        verbose_name='Title',
        max_length=50,
    )
    posts = models.ManyToManyField(
        verbose_name='Where It Is Used',
        to=Post,
        related_name='attachments',
        through='PostContent'
    )


class PostContent(models.Model):
    post = models.ForeignKey(
        verbose_name='Post',
        to=Post,
        on_delete=models.CASCADE,
        related_name='+',
    )
    attachment = models.ForeignKey(
        verbose_name='Content',
        to=AbstractContent,
        on_delete=models.CASCADE,
        related_name='+',
    )
    position = models.FloatField(
        verbose_name='Attachment\'s Position',
    )
    # it's float to easier put some content between
    # any two positions in post, for example if we
    # wanna insert a new content between 2 and 3
    # positions we can assign value 2.5

    views_count = models.PositiveIntegerField(
        verbose_name='Views Count',
        default=0,
    )


class TextContent(AbstractContent):
    content = models.TextField(
        verbose_name='Content',
    )


class FileContent(AbstractContent):
    pass


class VideoContent(FileContent):
    pass


class AudioContent(FileContent):
    pass


class AbstractFile(PolymorphicModel):
    file = models.FileField(
        verbose_name='File',
    )
    content = models.ForeignKey(
        verbose_name='Content using thisFile',
        to=FileContent,
        on_delete=models.CASCADE,
        related_name='files',
    )


class SubtitleFile(AbstractFile):
    # Extension abilities:
    #  - can add specific fields, for example: language
    #  - can add several subtitle files with different
    #    languages to one VideoContent instance
    pass


class VideoFile(AbstractFile):
    # Extension abilities:
    #  - can add specific fields, for example: quality
    #  - can add several video files with different
    #    quality to one VideoContent instance
    #  - for other-languages voice actings can describe
    #    certain model based on AbstractFile
    pass


class AudioFile(AbstractFile):
    # Extension abilities:
    #  - can add several audio files with different
    #    bitrates to one AudioContent instance
    #  - can add text file with transcript of audio
    bitrate = models.PositiveSmallIntegerField(
        verbose_name='Bitrate',
    )
