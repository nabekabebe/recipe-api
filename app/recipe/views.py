"""
Recipe api view
"""

from rest_framework import (viewsets, authentication, permissions, mixins)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
    IngredientSerializer
)
from core.models import (
    Recipe,
    Tag,
    Ingredient
)


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


class TagViewSet(
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """ Tag list api view for authenticated users"""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrive tags per authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class IngredientViewSet(
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """ Ingredient list api view for authenticated users"""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrive ingredients per authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
