"""
Recipe api view
"""
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes
)

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs'
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs'
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """ Recipe list api view for authenticated users"""

    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrive recipes per authenticated user"""
        tags_params = self.request.query_params.get('tags', None)
        ingredients_params = self.request.query_params.get('ingredients', None)

        if tags_params is not None:
            tags = tags_params.split(',')
            self.queryset = self.queryset.filter(tags__id__in=tags)

        if ingredients_params is not None:
            ingredients = ingredients_params.split(',')
            self.queryset = self.queryset.filter(
                ingredients__id__in=ingredients)

        return self.queryset.filter(
            user=self.request.user).order_by('-id').distinct()

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT,
                enum=[0, 1],
                description='Filter by assigned items to recipe'
            )
        ]
    )
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
        """Retrive tags/ingredients per authenticated user"""
        assign_param = self.request.query_params.get('assigned_only', 0)
        if bool(assign_param):
            self.queryset = self.queryset.filter(recipe__isnull=False)
        return self.queryset.filter(
            user=self.request.user).order_by('-name').distinct()


class TagViewSet(BaseRecipeAttrViewSet):
    """ Tag list api view for authenticated users"""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """ Ingredient list api view for authenticated users"""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
