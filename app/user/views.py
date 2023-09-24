"""
Views for user endpoints
"""

from rest_framework import generics
from user.serializers import UserSerializer


class UserCreateView(generics.CreateAPIView):
    """ Create a new user in the system """
    serializer_class = UserSerializer
