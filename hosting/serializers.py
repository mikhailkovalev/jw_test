from django.contrib.auth.models import (
    User,
)
from rest_framework.serializers import (
    CharField,
    HyperlinkedModelSerializer,
    ModelSerializer,
    SerializerMethodField,
)
from rest_polymorphic.serializers import (
    PolymorphicSerializer,
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


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
        )


class PostSerializer(HyperlinkedModelSerializer):
    publisher = UserSerializer()

    class Meta:
        model = Post
        fields = (
            'publisher',
            'url',
        )


class AbstractContentSerializer(ModelSerializer):
    class Meta:
        model = AbstractContent
        fields = (
            'title',
        )


class TextContentSerializer(AbstractContentSerializer):
    class Meta(AbstractContentSerializer.Meta):
        model = TextContent
        fields = AbstractContentSerializer.Meta.fields + (
            'content',
        )


class AbstractFileSerializer(ModelSerializer):
    class Meta:
        fields = (
            'file',
        )


class AudioFileSerializer(AbstractFileSerializer):
    class Meta(AbstractFileSerializer.Meta):
        model = AudioFile
        fields = AbstractFileSerializer.Meta.fields + (
            'bitrate',
        )


class SubtitleFileSerializer(AbstractFileSerializer):
    class Meta(AbstractFileSerializer.Meta):
        model = SubtitleFile


class VideoFileSerializer(AbstractFileSerializer):

    class Meta(AbstractFileSerializer.Meta):
        model = VideoFile


class FileContentSerializer(AbstractContentSerializer):
    class Meta(AbstractContentSerializer.Meta):
        fields = AbstractContentSerializer.Meta.fields + (
            'files',
        )


class AudioContentSerializer(FileContentSerializer):
    files = AudioFileSerializer(read_only=True, many=True)

    class Meta(FileContentSerializer.Meta):
        model = AudioContent


class VideoContentSerializer(FileContentSerializer):
    files = SerializerMethodField('get_videofiles_only')
    subtitles = SerializerMethodField('get_subtitles')

    class Meta(FileContentSerializer.Meta):
        model = VideoContent
        fields = FileContentSerializer.Meta.fields + (
            'subtitles',
        )

    def get_videofiles_only(self, obj):
        return self._get_specific_files(
            obj=obj,
            file_type=VideoFile,
            serializer_cls=VideoFileSerializer,
        )

    def get_subtitles(self, obj):
        return self._get_specific_files(
            obj=obj,
            file_type=SubtitleFile,
            serializer_cls=SubtitleFileSerializer,
        )

    def _get_specific_files(self, obj, file_type, serializer_cls):
        return tuple(
            serializer_cls(file).data
            for file in obj.files.all()
            if isinstance(file, file_type)
        )


class PostContentSerializer(ModelSerializer):
    title = CharField(source='attachment.title')

    class Meta:
        model = PostContent
        fields = (
            'title',
            'position',
            'views_count',
        )


class ContentPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        TextContent: TextContentSerializer,
        AudioContent: AudioContentSerializer,
        VideoContent: VideoContentSerializer,
    }


class PostDetailedSerializer(PostSerializer):
    attachments = SerializerMethodField('get_attachments')

    class Meta(PostSerializer.Meta):
        model = Post
        fields = PostSerializer.Meta.fields + (
            'attachments',
        )

    def get_attachments(self, obj):
        post_attachments = PostContent.objects.filter(
            post=obj,
        )
        return tuple(
            {
                **PostContentSerializer(post_attachment).data,
                **ContentPolymorphicSerializer(post_attachment.attachment).data,
            }
            for post_attachment in post_attachments
        )
