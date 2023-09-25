"""
Recipe api view
"""

from rest_framework import viewsets, authentication, permissions

from recipe.serializers import (
    RecipeSerializer, RecipeDetailSerializer
)
from core.models import Recipe


class RecipeViewSet(viewsets.ModelViewSet):
    """ Recipe list api view for authenticated users"""

    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrive recipes per authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Get serializer class"""
        if self.action == 'list':
            return RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)
