from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient serializer"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Recipe Serializer"""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "description",
            "time_minutes",
            "price",
            "link",
            "tags",
            "ingredients"
        ]
        read_only_fields = ["id"]

    def _get_or_create_tags(self, tags, recipe):
        """ Get or create tags and assign them to recipe"""
        auth_user = self.context['request'].user

        for tag in tags:
            newTag, isCreated = Tag.objects.get_or_create(
                user=auth_user, **tag)
            recipe.tags.add(newTag)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """ Get or create ingredients and assign them to recipe"""
        auth_user = self.context['request'].user

        for tag in ingredients:
            newTag, isCreated = Ingredient.objects.get_or_create(
                user=auth_user, **tag)
            recipe.ingredients.add(newTag)

    def create(self, validated_data):
        """ Create and return a recipe"""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])

        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """ Update and return recipe"""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Recipe detail serializer"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]
