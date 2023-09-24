"""
Views for user endpoints
"""

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import generics
from user.serializers import UserSerializer, AuthSerializer
from rest_framework.settings import api_settings


class UserCreateView(generics.CreateAPIView):
    """ Create a new user in the system """
    serializer_class = UserSerializer


class AuthTokenView(ObtainAuthToken):

    serializer_class = AuthSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
