"""
Test for ingredient api
"""

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


def get_ingredient_detial_url(ingredient_id):
    """Create and return tag detail url"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='user@email.com', password='testpass123'):
    """Create and return test user"""
    return get_user_model().objects.create_user(email=email, password=password)


def create_ingredient(user, name='Lettuce'):
    """Create and return an ingredient"""
    return Ingredient.objects.create(user=user, name=name)


class PublicIngredientApiTests(TestCase):
    """Test ingredient api for unauthenticated users"""

    def setUp(self):
        self.client = APIClient()

    def test_get_ingredient_error(self):
        """Test retrieving ingredient for non loggedin user error"""

        resp = self.client.get(INGREDIENT_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test ingredient api for authenticated users"""

    def setUp(self):
        self.user = create_user(email='auth')
        self.client = APIClient()

        self.client.force_authenticate(user=self.user)

    def test_get_ingredients_successful(self):
        """Test getting all ingredients success"""

        create_ingredient(user=self.user)
        create_ingredient(user=self.user, name="Tomato")

        resp = self.client.get(INGREDIENT_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(resp.data, serializer.data)

    def test_get_ingredients_per_user(self):
        """ Test retrieving ingredients that belong to logged in user """
        otherUser = create_user(email='other@example.com')

        create_ingredient(user=otherUser)
        create_ingredient(user=self.user, name='some tag')

        resp = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.filter(
            user=self.user).order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_update_ingredient_successful(self):
        """Test updating an ingredient"""

        ingredient = create_ingredient(user=self.user)
        payload = {'name': 'Updated Ingredient'}
        resp = self.client.put(
            get_ingredient_detial_url(ingredient.id), payload)

        ingredient.refresh_from_db()

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(str(ingredient), payload['name'])

    def test_delete_ingredient_successful(self):
        """Test deleting an ingredient"""

        ingredient = create_ingredient(user=self.user)
        resp = self.client.delete(get_ingredient_detial_url(ingredient.id))

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())

    def test_delete_other_user_ingredient_error(self):
        """Test deleting other user's ingredient should error"""
        otherUser = create_user(email='other@example.com')
        ingredient = create_ingredient(user=otherUser)

        resp = self.client.delete(get_ingredient_detial_url(ingredient.id))

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_ingredients_by_assigned(self):
        """Test retrieving ingredients that are assigned to recipes"""

        recipe = Recipe.objects.create(
            title='Recipe 1',
            time_minutes=5,
            price=5.00,
            user=self.user,
            description='Recipe 1 description'
        )

        ingredient = create_ingredient(user=self.user, name='ingredient 1')
        ingredient2 = create_ingredient(user=self.user, name='ingredient 2')
        recipe.ingredients.add(ingredient)

        resp = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        s = IngredientSerializer(ingredient)
        s2 = IngredientSerializer(ingredient2)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertIn(s.data, resp.data)
        self.assertNotIn(s2.data, resp.data)

    def test_filter_ingredients_unique(self):
        """Test filtering ingredients returns unique items"""

        recipe1 = Recipe.objects.create(
            title='Recipe 1',
            time_minutes=5,
            price=5.00,
            user=self.user,
            description='Recipe 1 description'
        )
        recipe2 = Recipe.objects.create(
            title='Recipe 1',
            time_minutes=5,
            price=5.00,
            user=self.user,
            description='Recipe 1 description'
        )

        ingredient = create_ingredient(user=self.user, name='ingredient 1')
        create_ingredient(user=self.user, name='ingredient 2')
        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        resp = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
