"""
User model serialzier
"""

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
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


class AuthSerializer(serializers.Serializer):
    """ Serializer for user authentication """

    email = serializers.EmailField()
    password = serializers.CharField(
        trim_whitespace=False,
        style={'input_type': 'password'},
    )

    def validate(self, attrs):
        """ Validate and authenticate user """

        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password,
        )

        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user

        return attrs
