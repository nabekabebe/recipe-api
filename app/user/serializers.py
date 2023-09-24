"""
User model serialzier
"""

from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer


class UserSerializer(ModelSerializer):
    """ Serializer for user model """

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {
            'password':  {'write_only': True, 'min_length': 8}
        }

    def create(self, validated_data):
        """ Create a new user and return it """
        return get_user_model().objects.create_user(**validated_data)
