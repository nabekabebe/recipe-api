"""
Test for recipe API
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer, RecipeDetailSerializer
)


RECIPE_URL = reverse('recipe:recipe-list')

RECIPE_PAYLOAD = {
        'title': 'Sample Recipe',
        'description': 'Sample Description',
        'time_minutes': 10,
        'price': Decimal('5.00'),
        'link': 'http://exmple.com/recipe.pdf'
    }


def recipe_detail_url(recipe_id):
    """ Return recipe detail url """
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **data):
    """ Create and return recipe """

    RECIPE_PAYLOAD.update(data)

    return Recipe.objects.create(user=user, **RECIPE_PAYLOAD)


def create_user(**data):
    """Create and return a user"""
    return get_user_model().objects.create_user(**data)


class PublicRecipeApiTests(TestCase):
    """Test for unauthenticated users"""

    def setUp(self):
        self.client = APIClient()

    def test_recipe_get_error_for_unauthenticated_user(self):
        """ Test recipes cannot be retrieved by unauthenticated user """

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """ Test authenticated recipe API access """

    def setUp(self):
        self.user = create_user(
            email='recipe@example.com',
            password='testpass123'
            )
        self.client = APIClient()

        self.client.force_authenticate(user=self.user)

    def test_recipe_get_all_recipes(self):
        """Test getting all recipes for authenticated user"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        resp = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_recipe_get_per_user(self):
        """Testing getting recipes that belong to loggedin user"""
        otherUser = create_user(
            email='other@example.com',
            password='testpass123'
        )
        create_recipe(user=otherUser)
        create_recipe(user=self.user)

        resp = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), len(serializer.data))

    def test_recipe_detail_view(self):
        """Test viewing a recipe detail"""
        recipe = create_recipe(user=self.user)
        url = recipe_detail_url(recipe.id)

        resp = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_recipe_create(self):
        """Test create a recipe test"""

        resp = self.client.post(RECIPE_URL, RECIPE_PAYLOAD)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=resp.data['id'])

        # Check if the recipe is created with the correct data
        for key, value in RECIPE_PAYLOAD.items():
            self.assertEqual(value, getattr(recipe, key, None))

        # Check if the recipe is created for the loggedin user
        self.assertEqual(recipe.user, self.user)

    def test_recipe_partial_update(self):
        """Test updating a recipe with patch"""
        recipe = create_recipe(user=self.user)
        payload = {'title': 'New Title'}
        resp = self.client.patch(recipe_detail_url(recipe.id), payload)

        recipe.refresh_from_db()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.description, RECIPE_PAYLOAD['description'])

    def test_recipe_full_update(self):
        """Test updating a recipe with put"""

        recipe = create_recipe(user=self.user)
        payload = {
            'title': 'New Title',
            'description': 'New Description',
            'time_minutes': 20,
            'price': Decimal('10.00'),
            'link': 'http://exmple.com/new_recipe.pdf'
        }
        resp = self.client.put(recipe_detail_url(recipe.id), payload)

        recipe.refresh_from_db()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Check if the recipe is created with the correct data
        for key, value in payload.items():
            self.assertEqual(value, getattr(recipe, key, None))

    def test_get_other_user_recipe_error(self):
        """Test that cuurent user cannot view other user recipe"""

        otherUser = create_user(
            email='other@example.com',
            password='testpass123')
        recipe = create_recipe(user=otherUser)

        resp = self.client.get(recipe_detail_url(recipe.id))

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_recipe_success(self):
        """Test deleting a recipe"""

        recipe = create_recipe(user=self.user)

        resp = self.client.delete(recipe_detail_url(recipe.id))

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_update_recipe_owner_should_not_work(self):
        """Test updating user through recipe should not work"""

        otherUser = create_user(
            email='other@example.com',
            password='testpass123')

        recipe = create_recipe(user=self.user)

        self.client.patch(
            recipe_detail_url(recipe.id),
            {'user': otherUser.id}
        )
        recipe.refresh_from_db()
        self.assertNotEqual(recipe.user.id, otherUser.id)
