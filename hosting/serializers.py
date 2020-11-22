from django.contrib.auth.models import (
    User,
)
from rest_framework.serializers import (
    HyperlinkedModelSerializer,
    ModelSerializer,
)

from .models import (
    Post,
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
