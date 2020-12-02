from django.db import models
from django.conf import (
    settings,
)

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

    def get_short_title(self):
        result = self.title
        if len(result) > settings.POST_PREVIEW_LEN:
            cut_idx = (
                settings.POST_PREVIEW_LEN - len(settings.POST_PREVIEW_TRAILING))
            result = ''.join((
                result[:cut_idx],
                settings.POST_PREVIEW_TRAILING,
            ))

        return result

    def __str__(self):
        return self.get_short_title()


class PostContent(models.Model):
    class Meta:
        ordering = (
            'position',
        )
    post = models.ForeignKey(
        verbose_name='Post',
        to=Post,
        on_delete=models.CASCADE,
        related_name='post_contents',
    )
    attachment = models.ForeignKey(
        verbose_name='Content',
        to=AbstractContent,
        on_delete=models.CASCADE,
        related_name='+',
    )
    position = models.PositiveIntegerField(
        verbose_name='Attachment\'s Position',
        default=0,
        blank=False,
        null=False,
    )

    views_count = models.PositiveIntegerField(
        verbose_name='Views Count',
        default=0,
    )

    def __str__(self):
        return '{attachment_type}: {attachment_name}'.format(
            attachment_type=self.attachment.__class__.__name__,
            # attachment_type=self.attachment._meta.model_name,
            attachment_name=str(self.attachment),
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

    def __str__(self):
        return str(self.file)


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
