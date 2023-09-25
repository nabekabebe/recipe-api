from rest_framework import serializers
from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Recipe Serializer"""

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "description",
            "time_minutes",
            "price",
            "link"
        ]
        read_only_fields = ["id"]


class RecipeDetailSerializer(RecipeSerializer):
    """Recipe detail serializer"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]
