"""
Views for user endpoints
"""

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import generics, authentication, permissions
from user.serializers import UserSerializer, AuthSerializer
from rest_framework.settings import api_settings


class CreateUserView(generics.CreateAPIView):
    """ Create a new user in the system """
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):

    serializer_class = AuthSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """ Handle authenticated users """

    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """ Get loggedin user from request """
        return self.request.user
