"""
Recipe api view
"""

from rest_framework import (viewsets, authentication, permissions, mixins)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeImageSerializer
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
        if self.action == 'upload_image':
            return RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
                None,
                status=status.HTTP_400_BAD_REQUEST
            )


class BaseRecipeAttrViewSet(
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """Base class for recipe attributes view set"""

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrive tags per authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeAttrViewSet):
    """ Tag list api view for authenticated users"""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """ Ingredient list api view for authenticated users"""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
